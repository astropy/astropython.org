from django.shortcuts import Http404
from django.db.models import Q
from django.utils.encoding import smart_text
import random
from slugify import slugify

from .forms import *
from .models import *

from bs4 import BeautifulSoup

import json

import os
import feedparser
import pytz

from dateutil.parser import parse
from datetime import datetime

from operator import attrgetter
from itertools import chain

def get_model(name):
    if name=='tutorials':
        return Tutorial
    elif name=="snippets":
        return Snippet
    elif name=="education":
        return EducationalResource
    elif name=="wiki":
        return Wiki
    elif name=="announcements":
        return Announcement
    elif name=="news":
        return News
    elif name=="blog":
        return Blog
    elif name=="packages":
        return Package
    elif name=="events":
        return Event

def get_section(model):
    if model==Tutorial:
        return 'tutorials'
    elif model==Snippet:
        return "snippets"
    elif model==EducationalResource:
        return "education"
    elif model==Wiki:
        return "wiki"
    elif model==Announcement:
        return "announcements"
    elif model==News:
        return "news"
    elif model==Blog:
        return "blog"
    elif model==Package:
        return "packages"
    elif model==Event:
        return "events"

def get_name(name):
    if name=='tutorials':
        return "Tutorials"
    elif name=="snippets":
        return "Code Snippets"
    elif name=="education":
        return "Educational Resources"
    elif name=="wiki":
        return "Wiki Pages"
    elif name=="announcements":
        return "Announcements"
    elif name=="news":
        return "News Articles"
    elif name=="blog":
        return "Blog Posts"
    elif name=="packages":
        return "Packages"
    elif name=="events":
        return "Events"

def get_exclude_fields(model):
        return ['slug','authors','state','published']

def get_create_form(request,exclude_fields,model,kwargs):
    if 'slug' in kwargs:
        obj=model.objects.get(slug=kwargs['slug'])
        if check_editing_permission(request.user,obj):
            return PostForm(model,exclude_fields,'create',request.POST or None,instance=obj)
        else:
            raise Http404
    return PostForm(model,exclude_fields,'create',request.POST or None)


def check_editing_permission(user,obj):
    if ((not user in obj.authors.all()) or (obj.state=="submitted") ):
        return False
    return True

def check_viewing_permission(user,obj):
    if(obj.state=="raw"):
        if not request.user in obj.authors.all():
            return False
    return True
def generate_temp_slug(model):
    slug="%0.12d" % random.randint(0,999999999999)
    while (model.objects.filter(slug=slug).exists() or model.unmoderated_objects.filter(slug=slug).exists()):
        slug="%0.12d" % random.randint(0,999999999999)
    return slug

def generate_final_slug(model,title):
    slug=slugify(title)
    while (model.objects.filter(slug=slug).exists() or model.unmoderated_objects.filter(slug=slug).exists()):
        slug=slug+str(random.randrange(1,1000+1))
    return slug

def get_slug(request,model,title,kwargs):
    if 'save' in request.POST:
        if 'slug' not in kwargs:
            return generate_temp_slug(model)
        else:
            return kwargs['slug']
    elif 'submit' in request.POST:
        return generate_final_slug(model,title)

def set_state(request,form):
    if 'submit' in request.POST:
        return "submitted"
    elif 'save' in request.POST:
        for field in form.fields:
            form.fields[field].required = False
        return "raw"

def get_user(request):
    user=request.user
    if user.is_authenticated():
        return user
    else:
        u=User.objects.get_or_create(username="Anonymous")
        return u[0]

def get_section_models(name):
    if name=="all":
        return [Tutorial,Snippet,Wiki,Announcement,News,Blog,EducationalResource,Package,Event]
    elif name=="tl":
        return[Tutorial,Snippet,Wiki,EducationalResource]
    elif name=="forum":
        return [Announcement,News,Blog,Event]

def get_all_objects(section):
    object_list=[]
    model_list=get_section_models(section)
    for model in model_list:
            object_list=chain(object_list,(model.objects.filter(state="submitted").order_by('published').all()))
    object_list = sorted(object_list, key=attrgetter('published'),reverse=True)
    return object_list

def get_all_native_objects(section):
    object_list=[]
    model_list=get_section_models(section)
    for model in model_list:
            object_list=chain(object_list,(model.objects.filter(~Q(authors__username__startswith = "Feed")).filter(state="submitted").order_by('published').all()))
    object_list = sorted(object_list, key=attrgetter('published'),reverse=True)
    return object_list

def update_feeds():
    feeds=Feed.objects.all()
    for feed in feeds:
        model=get_model(feed.section)
        contents=feedparser.parse(feed.url)
        if not feed.notes:
            try:
                feed.notes=contents['feed']['description']
                feed.save()
            except:
                pass
        obj=model()
        for entry in contents.entries:
            try:
                if model.objects.filter(title=entry.title).exists() or model.unmoderated_objects.filter(title=entry.title).exists():
                    continue
            except:
                obj.delete()
                if model.objects.filter(title=entry.title).exists() or model.unmoderated_objects.filter(title=entry.title).exists():
                    continue
            obj=model(title=entry.title)
            if 'content' in entry:
                if 'value' in entry.content[0]:
                    soup = BeautifulSoup(entry.content[0]['value'], 'html.parser')
                    k=soup.prettify()
                    obj.body=k.encode('ascii', 'ignore')
                    obj.body=obj.body.replace("\n","")
                    obj.body=obj.body.replace("\"","\'")
                    obj.body=json.dumps(obj.body)
                else:
                    soup = BeautifulSoup(entry.content, 'html.parser')
                    k=soup.prettify()
                    obj.body=k.encode('ascii', 'ignore')
                    obj.body=obj.body.replace("\n","")
                    obj.body=obj.body.replace("\"","\'")
                    obj.body=json.dumps(obj.body)
            elif 'description' in entry:
                k=entry.description
                obj.body=k.encode('ascii', 'ignore')
                obj.body=obj.body.replace("\n","")
                obj.body=obj.body.replace("\"","\'")
                obj.body=json.dumps(obj.body)
            elif 'summary' in entry:
                k=entry.summary
                obj.body=k.encode('ascii', 'ignore')
                obj.body=obj.body.replace("\n","")
                obj.body=obj.body.replace("\"","\'")
                obj.body=json.dumps(obj.body)
            obj.input_type='WYSIWYG'
            slug=slugify(entry.title)+str(random.randrange(1,1000+1))
            while (model.objects.filter(slug=slug).exists()):
                slug=slug+str(random.randrange(1,1000+1))
            obj.slug=slug
            obj.state="submitted"
            try:
                if 'published' in entry:
                    obj.published=(parse(entry.published)).replace(tzinfo=None)
                elif 'pubDate' in entry:
                    obj.published=(parse(entry.pubDate)).replace(tzinfo=None)
                elif 'updated' in entry:
                    obj.published=(parse(entry.updated)).replace(tzinfo=None)
            except:
                pass
            try:
                obj.save()
            except:
                obj.body="a"
                obj.slug="g"
                obj.save()
                #obj.save()
                obj.delete()
                continue
            user=User.objects.get_or_create(username=('Feed : '+feed.title))
            obj.authors.add(user[0])