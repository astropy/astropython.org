"""
This file handles all the abckground computation that happens between calling any URL and obtaining a Template Response

Note : Context refers to the items we wish to pass to our templates.
"""
from django.shortcuts import render,HttpResponseRedirect,Http404,RequestContext
from django.contrib.auth import logout
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.db.models.functions import Lower

from moderation.helpers import automoderate
from django.core.mail import send_mail

import feedparser
import secretballot
import watson
import random
from datetime import datetime

from .forms import *
from .models import *
from .utilities import *
from taggit.models import Tag,TaggedItem

"""
Generates our landing page / homepage....
Only those slider images are fetched from the Database that fall in the specified date range
(Each image has a date range between which it will be displayed on the website
Images without date range are displayed forever !)
After fetching the images it shuffles them , so everytime a different image appears on the homepage

This is followed by fetching latest posts from Teach & Learn, Forum and Packages Section and passing everything to the templates

"""
def home(request):
    sp=[]
    slider_list=Slider.objects.filter(Q(start_date_time__lte=datetime.now()),(Q(end_date_time__gte=datetime.now())|Q(end_date_time__isnull=True))).all()
    for s in slider_list:
        sp.append(s)
    shuffle_images=sorted(sp, key=lambda k: random.random()) #Shuffle with a random key
    sp=shuffle_images
    context = {'g_message':'< A Google Summer of Code, 2015 Creation />','sliders':sp,'tl_posts':get_all_objects("tl")[:8],'forum_posts':get_all_objects("forum")[:8],'package_posts':Package.objects.filter(state="submitted").order_by('-published').all()[:4]}
    return render(request, 'index.html', context)

"""
View that logs out a logged in user
"""
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))

"""
View that utilizes the creation form to add new articles to the website
"""
def create(request,section,**kwargs):
    model=get_model(section)#Identify the type of article - Blogs,Tutorials,etc
    name =get_name(section) #Fetch generic name
    tags=[]#List to store all tags that are currently associated with the article type
    t=model.tags.all()
    for tag in t:
        tags.append(tag.name)
    tags= sorted(tags, key=lambda s: s.lower())#Sort tags in alphabetical order
    exclude_fields = get_exclude_fields(model)#Hide secret fields
    form = get_create_form(request,exclude_fields,model,kwargs)#Fetch form
    if request.method=="POST":#If user has POSTed anything on our server
        state=set_state(request,form)#Raw State if user has not pressed "Submit" yet !
        if form.is_valid():#If form is valid
            instance=form.save(commit=False)#save form data in a model object, but do not commit to DB
            slug = get_slug(request,model,instance.title,kwargs)#Get Slug
            user=get_user(request) #Get author
            instance.state=state #Store State - "Raw" (saved, not submitted) or "Submitted"
            instance.slug=slug #Store slug
            instance.save() #Commit instance to DB
            instance.authors.add(user) #Add authors
            form.save_m2m()
            automoderate(instance,user) # Add to Moderation
            #Send email to moderators
            try:
                if instance.state=="submitted":
                    subject="New AstroPython Post !"
                    message="A new post to AstroPython"
                    html_m='<hr /><h2 style="text-align:center"><code><tt><span style="font-family:trebuchet ms,helvetica,sans-serif"><strong>AstroPython - Python for Astronomers</strong></span></tt></code></h2><hr /><p>A Post "'+instance.title+'"&nbsp;&nbsp;has&nbsp;been added. It is waiting for moderation !</p><p>Access it <a href="http://www.astropython.org'+instance.get_absolute_url()+'">here</a> !</p><p>Thank you,</p><p><strong>AstroPython Team</strong></p><hr /><p style="text-align:right"><span style="font-size:10px">Currently , you cannot unsubscribe to these emails</span></p>'
                    from_email="notifications@astropython.org"
                    send_mail(subject,message,from_email,["amanjjw@gmail.com","taldcroft@gmail.com"], fail_silently=False,html_message=html_m)
            except:
                print "No Email Provided"
            return render(request,'complete.html',{'section':section,'slug':slug,'state':state,'name':name})
    return render(request,'creation.html',{'form':form,'name':name,'tags': tags})

"""
To view a single model instance
"""
def single(request,section,slug,**kwargs):
    model=get_model(section)#Identify the type of article - Blogs,Tutorials,etc
    name=get_name(section) # Get generic name
    tags=model.tags.all() #Fetch all tags for edit form
    obj=model.objects.get(slug=slug) #Fetch the article being demanded
    mode="display" # Mode is "edit" when the user wished to edit any article
    if request.method=="GET" and 'edit' in request.GET:
        edit=request.GET['edit']
        edit_field=edit.split(',')#split fieds user wished to edit. One user may want to edit more than 1 field at once
        request.session['edit_field']=edit_field#Store fields in session
        request.session.modified = True
        form= PostForm(model,edit_field,'edit',instance=obj)#Fetch edit form
        mode="edit" #Change mode
    elif request.method=="POST":
        form= PostForm(model,request.session['edit_field'],'edit',request.POST,instance=obj)
        mode="edit"
        if form.is_valid():#If edit is valid
            instance=form.save(commit=False)#Commit to DB
            user=get_user(request)#Get  user
            instance.save()#Save instance
            form.save_m2m()
            automoderate(instance,user)#Send to moderation
            return HttpResponseRedirect(reverse('single',kwargs={'section':section,'slug':obj.slug}))
    else:
        form=None#If no edit is there, just display the article
    recent=model.objects.all().filter(state="submitted").order_by('-published')[:5]
    return render(request,'single.html',{'obj':obj,'section':section,'full_url':request.build_absolute_uri(),"mode":mode,"form":form,"tags":tags,'page':'single','recent':recent})

"""
Method for upvoting/downvoting articles
"""
def vote(request,section,choice,slug):
    model=get_model(section)#Identify the type of article - Blogs,Tutorials,etc
    obj=model.objects.get(slug=slug)#get slug for article to vote
    v=model.objects.from_request(request).get(pk=obj.pk)
    token=request.secretballot_token#Get unique hash for each IPAddress so that users can vote only once
    if(choice=='upvote'):
        t=1
    else:
        t=-1
    if v.user_vote==t:
        obj.remove_vote(token)#Voting the same article twice removes the vote
    else:
        obj.add_vote(token,t)
    return HttpResponseRedirect(reverse('single',kwargs={'slug':slug,'section':section}))

"""
General listing of all sections
"""

def all(request,section,**kwargs):
    model=get_model(section)#Identify the type of article - Blogs,Tutorials,etc
    name=get_name(section)# Get generic name
    """
    if(model==Tutorial or model==EducationalResource or model==Wiki or model==Snippet):
        s_area="tl"
    elif(model==Blog or model==News or model==Announcement or model==Event):
        s_area="forum"
    elif(model==Package):
        s_area="packages"
    else:
    """
    t=None
    s=None
    f=None
    message=""
    if 'sort' in request.GET:#If any sort parameters exist
        sort=request.GET['sort']
        s=sort#Store sort parameters in s
        message+="Ordered by "+sort+"   "
        #Sort according to the user's choice
        if sort=="ratings":
            obj_list=model.objects.all().filter(state="submitted").order_by('-total_upvotes')
        elif sort=="alphabetical":
             obj_list=model.objects.all().filter(state="submitted").order_by(Lower('title'))
        else:
            obj_list=model.objects.all().filter(state="submitted").order_by('-published')
    else:
        if section=="packages": #Default way to display packages is alphabetically
             obj_list=model.objects.all().filter(state="submitted").order_by(Lower('title'))
        else:
            obj_list=model.objects.all().filter(state="submitted").order_by('-published')
    if 'tags' in request.GET:#If filtering by tags is required
        tags=request.GET['tags']
        t=tags
        if message=="":
            message+="Filtered by tags : "+tags
        else:
            message+=",Filtered by tags : "+tags
        tag=tags.split(',')
        for tag_elem in tag:
            tag_list=[]
            tag_list.append(tag_elem)
            obj_list=obj_list.filter(tags__name__in=tag_list).distinct()
    if 'filter' in request.GET:
        f=request.GET['filter']
        message+="(Showing "+f+" posts)"
        if f=='native':
            obj_list=obj_list.filter(~Q(authors__username__startswith = "Feed")).distinct()
        elif f=='feeds':
            obj_list=obj_list.filter(authors__username__startswith = "Feed").distinct()
        elif f=='recommended':
            cat=PackageCategory.objects.get(name="Recommended")
            obj_list=obj_list.filter(category=cat)
        elif f=='active':
            cat=PackageCategory.objects.get(name="Active")
            obj_list=obj_list.filter(category=cat)
        elif f=='deprecated':
            cat=PackageCategory.objects.get(name="Deprecated")
            obj_list=obj_list.filter(category=cat)
    length=len(obj_list)
    if section=="packages":
        paginator = Paginator(obj_list,100)
    else:
        paginator = Paginator(obj_list,15)
    page = request.GET.get('page')
    try:
        obj=paginator.page(page)
    except:
        obj=paginator.page(1)
    tags=[]
    for ob in obj_list:
        tags += ob.tags.all()
    tags=list(set(tags))
    recent=model.objects.all().filter(state="submitted").order_by('-published')[:5]
    get={'tags':t,'filter':f,'sort':s}
    context = {'name':name,'obj':obj,'section':section,'length':length,'message':message,'tags':tags,'range':range(1,obj.paginator.num_pages+1),'page':'all','recent':recent,'get':get}
    return render(request,'all.html',context)

def search(request):
    if request.GET['q']:
        name="All Sections"
        section="all"
        query=request.GET['q']
        if 'section' in request.GET:
            section=request.GET['section']
            if section=="all":
                results=watson.search(query)
            elif section=="tl":
                name="Teach and Learn"
                results=watson.search(query,models=tuple([Tutorial,EducationalResource,Wiki,Snippet]))
            elif section=="forum":
                name="Forum"
                results=watson.search(query,models=tuple([Announcement,Event,Blog,News]))
            else:
                sec=[]
                model=get_model(section)
                name=get_name(section)
                sec.append(model)
                results=watson.search(query,models=tuple(sec))
        else:
            results=watson.search(query)
    else:
        return HttpResponseRedirect(reverse('home'))
    length=len(results)
    paginator = Paginator(results,15)
    page = request.GET.get('page')
    try:
        obj=paginator.page(page)
    except:
        obj=paginator.page(1)
    context = {'name':name,'obj':obj,'section':section,'length':length,'range':range(1,obj.paginator.num_pages+1),'query':query}
    return render(request,'search.html',context)

def written(request):
    u=request.user
    message=None
    tutorials_list=u.tutorial_set.all()
    announcements_list=u.announcement_set.all()
    blogs_list=u.blog_set.all()
    edresources_list=u.educationalresource_set.all()
    news_list=u.news_set.all()
    events_list=u.event_set.all()
    packages_list=u.package_set.all()
    snippets_list=u.snippet_set.all()
    wiki_list=u.wiki_set.all()
    if (len(tutorials_list)+len(announcements_list)+len(blogs_list)+len(edresources_list)+len(news_list)+len(events_list)+len(packages_list)+len(snippets_list)+len(wiki_list))==0:
        message="You do not have any posts yet !"
    context={'message':message,'tutorials_list':tutorials_list,'announcements_list':announcements_list,'blogs_list':blogs_list,'edresources_list':edresources_list,'news_list':news_list,'events_list':events_list,'packages_list':packages_list,'snippets_list':snippets_list,'wiki_list':wiki_list}
    return render(request,'written.html',context)

def timeline(request,section):
    obj_list=get_all_objects(section)
    t=None
    s=None
    f=None
    f2=0
    f3=0
    tags=[]
    tag=[]
    data=[]
    message=""
    if 'sort' in request.GET:
        sort=request.GET['sort']
        s=sort
        message+="Ordered by "+sort+"   "
        if sort=="ratings":
            obj_list = sorted(obj_list, key=attrgetter('total_upvotes'),reverse=True)
    if 'tags' in request.GET:
            tags_list=request.GET['tags']
            if message=="":
                message+="Filtered by tags : "+tags_list
            else:
                message+=",Filtered by tags : "+tags_list
            tag=tags_list.split(',')
    if 'filter' in request.GET:
                f=request.GET['filter']
                message+="(Showing "+f+" posts)"
    for ob in obj_list:
        f2=0
        f3=1
        if f:
            for a in ob.authors.all():
                if f=="native":
                    if a.username[:4] != "Feed":
                        f2=1
                elif f=="feeds":
                    if a.username[:4] == "Feed":
                        f2=1
                break
        else:
            f2=1
        if tag:
            for l in tag:
                if l not in ob.tags.names():
                    f3=0
        if f2==1 and f3==1:
            data.append(ob)
            tags += ob.tags.all()
    tags=list(set(tags))
    get={'tags':t,'filter':f,'sort':s}
    context = {'data':data,'section':section,'message':message,'tags':tags,'get':get}
    return render(request,'timeline.html',context)


def contact(request):
    if request.POST:
        form=ContactForm(request.POST)
        form.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def update_feed(request):
    update_feeds()
    return render(request,'complete.html',{'state':'feed_update','name':'Feed Update'})

def display_feed_list(request):
    obj_list=Feed.objects.all()
    length=len(obj_list)
    paginator = Paginator(obj_list,10)
    page = request.GET.get('page')
    try:
        obj=paginator.page(page)
    except:
        obj=paginator.page(1)
    context = {'name':'Feed List','obj':obj,'length':length,'range':range(1,obj.paginator.num_pages+1),'page':'all'}
    return render(request,'feed_list.html',context)

def try_python(request):
    return render(request,'try_python.html')
