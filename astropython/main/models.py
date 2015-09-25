"""
Define structures of models.
Each model is automatically translated to database schemas.
"""
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from colorfield.fields import ColorField

from taggit.managers import TaggableManager

import secretballot
import watson

from django.db.models.signals import post_save
from astropython.settings import STATE_CHOICES,INPUT_CHOICES,MEDIA_URL

PACKAGE_CHOICES = (
	('Recommended', 'Recommended'),
	('Others', 'Others'),
 )

SECTION_CHOICES = (
	('tutorials', 'Tutorials'),
	('snippets', 'Code Snippets'),
    ('education', 'Educational Resources'),
	('wiki', 'Wiki Pages'),
    ('announcements', 'Announcements'),
	('news', 'News'),
    ('blog', 'Blog'),
	('packages', 'Packages'),
    ('events', 'Events'),
 )

class BasePost(models.Model):
    title = models.CharField(max_length=200)#Title of the Post
    input_type=models.CharField(max_length=60,choices=INPUT_CHOICES,default="Markdown",verbose_name='Text Editor Choice',help_text='All current editor contents will be lost once editors are switched')
    abstract = models.TextField(blank=True,default="",help_text='Optional Summary of Post') #Short abstract of the tutorial
    authors = models.ManyToManyField(User,blank=True,null=True) # Collaborators of a tutorial
    body = models.TextField(blank=False,verbose_name='Page Body / Contents')
    slug = models.SlugField(unique=True) #Slug to a tutorial
    state = models.CharField(max_length=60,choices=STATE_CHOICES,default='raw') #State of a tutorial
    tags=TaggableManager(blank=True) #Tags
    created = models.DateTimeField(auto_now_add=True, auto_now=False)  # Date when first revision was created
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)  # Date when last revision was created (even if not published)
    published =models.DateTimeField(default= timezone.now)

    def __unicode__(self):
		return self.title


    class Meta:
        abstract=True

class Tutorial(BasePost):

    def get_absolute_url(self):
        return reverse('main.views.single',kwargs={'section':'tutorials','slug':self.slug})

class Snippet(BasePost):

    def get_absolute_url(self):
        return reverse('main.views.single',kwargs={'section':'snippets','slug':self.slug})

class Wiki(BasePost):

    def get_absolute_url(self):
        return reverse('main.views.single',kwargs={'section':'wiki','slug':self.slug})

class Announcement(BasePost):

    def get_absolute_url(self):
        return reverse('main.views.single',kwargs={'section':'announcements','slug':self.slug})

class News(BasePost):

    def get_absolute_url(self):
        return reverse('main.views.single',kwargs={'section':'news','slug':self.slug})

class Blog(BasePost):

    def get_absolute_url(self):
        return reverse('main.views.single',kwargs={'section':'blog','slug':self.slug})

class Package(BasePost):
    homepage=models.URLField(blank=True,verbose_name="Homepage URL")#URL : homepage of the packages
    docs = models.URLField(blank=True,verbose_name="URL to Docs")
    category=models.ManyToManyField('PackageCategory')

    def get_absolute_url(self):
        return reverse('main.views.single',kwargs={'section':'packages','slug':self.slug})

class EducationalResource(BasePost):
    start_date = models.DateTimeField(null=True, blank=True,help_text="Format : YYYY-MM-DD")#Date the course starts
    instructor_names = models.CharField(max_length=400,blank=True)#Names of Instructors
    website = models.URLField(blank=True,verbose_name='Course Website')#Website hosting the course, or having more info about the course
    contents = models.TextField(blank=True,verbose_name='Course Contents') #Syllabus or contents of the course
    background = models.TextField(blank=True,verbose_name='Recommended Background')#Recommended Backgroud
    faq=models.TextField(blank=True,verbose_name='Frequently Asked Questions')#FAQ if any
    language = models.CharField(max_length=200,blank=True,verbose_name='Language of Instruction')#Language in which course is to be conducted

    def get_absolute_url(self):
        return reverse('main.views.single',kwargs={'section':'education','slug':self.slug})

"""
Events model are associated with any future events that are planned
"""
class Event(models.Model):
    title = models.CharField(max_length=200)
    input_type=models.CharField(max_length=60,choices=INPUT_CHOICES,default="Markdown",verbose_name='Text Editor Choice',help_text='All current editor contents will be lost once editors are switched')
    authors = models.ManyToManyField(User,blank=True,null=True) # Collaborators of a tutorial
    body =models.TextField(blank=False,verbose_name='Page Body / Contents')
    location = models.CharField(max_length=1000,blank=True)
    website = models.URLField(blank=True)
    slug = models.SlugField(unique=True)
    state = models.CharField(max_length=60,choices=STATE_CHOICES,default='raw')
    tags=TaggableManager(blank=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)  # Date when first revision was created
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)  # Date when last revision was created (even if not published)
    start_date_time = models.DateTimeField(help_text="Format : YYYY-MM-DD")#start time
    end_date_time = models.DateTimeField(blank=True, null=True,help_text="Format : YYYY-MM-DD")#When dies the event end
    all_day_event = models.BooleanField(default=False)#If it is an all day event
    published =models.DateTimeField(null=True,blank=True)

    def __unicode__(self): #Format of representation of event
        date_format = '%Y-%m-%d %I:%M %p'
        if self.all_day_event:
            date_format = '%Y-%m-%d'
        return '%(n)s (%(d)s)' % {'n': self.title, 'd': self.start_date_time.strftime(date_format), }

    def active(self):#IF event is active
        if self.start_date_time and self.end_date_time:
            t = timezone.now()
            return self.start_date_time <= t and self.end_date_time >= t
        return False
    active.boolean = True

    def get_absolute_url(self):
        return reverse('main.views.single',kwargs={'section':'events','slug':self.slug})

class Contact(models.Model):
    username=models.CharField(max_length=60)
    email=models.CharField(blank=False,max_length=60)
    content=models.TextField(blank=False)

    def __unicode__(self):
		return self.content

class Feed(models.Model):
    title=models.CharField(max_length=120,blank=False)
    url=models.URLField(blank=False)
    section=models.CharField(max_length=60,choices=SECTION_CHOICES,default="blog")
    notes=models.TextField(blank=True)

    def __unicode__(self):
		return self.title

class PackageCategory(models.Model):
    name=models.CharField(max_length=60)

    def __unicode__(self):
        return self.name


class Slider(models.Model):
    image=models.ImageField(upload_to="slider_images/featured")
    credit=models.TextField(blank=True)
    description=models.TextField(blank=True)
    text_color=ColorField(default="#FFFFFF")
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    start_date_time = models.DateTimeField(default= timezone.now)#start time
    end_date_time = models.DateTimeField(blank=True, null=True,help_text="Optional End Date")

    def __unicode__(self):
        return self.description

    def get_image_url(self):
        return "%s/%s"%(MEDIA_URL,self.image)



secretballot.enable_voting_on(Tutorial)
secretballot.enable_voting_on(Snippet)
secretballot.enable_voting_on(Wiki)
secretballot.enable_voting_on(Announcement)
secretballot.enable_voting_on(News)
secretballot.enable_voting_on(Blog)
secretballot.enable_voting_on(Event)
secretballot.enable_voting_on(EducationalResource)
secretballot.enable_voting_on(Package)

watson.register(Tutorial)
watson.register(Snippet)
watson.register(Wiki)
watson.register(Announcement)
watson.register(News)
watson.register(Blog)
watson.register(EducationalResource)
watson.register(Package)
watson.register(Event)