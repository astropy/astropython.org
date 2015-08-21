"""
This script populated the database initially with the old ported data stored with the repo
"""
import os
import json
import datetime
import random
from slugify import slugify
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'astropython.settings')

#Setup Django and add all dependencies and code automatically
import django
django.setup()

from main.models import *

from django.contrib.auth.models import User,Group

"""
initialize() will be used to create Groups and other general entities in the future
"""
def initialize():

    Group.objects.get_or_create(name="Trusted Users")
    Group.objects.get_or_create(name="Preview Users")
    Group.objects.get_or_create(name="Banned Users")
    PackageCategory.objects.create(name="Recommended")
    PackageCategory.objects.create(name="Active")
    PackageCategory.objects.create(name="Deprecated")
    User.objects.create_superuser(username="admin",password="admin",email="test@example.com")
    ob=Wiki.objects.create(title="Wiki HomePage",input_type="WYSIWYG",state="submitted",slug="home",body=' "<h1>From our friends at Astrobetter !</h1>\
\
<p>This is the companion wiki to the <a class="wiki" href="http://www.astrobetter.com">AstroBetter Blog</a>. You can register (see right sidebar) to edit or comment on wiki pages. Please, share your expertise with us! If you have questions or do not know where to add your content, please email us at admin <a class="wiki" href="at">at</a> astrobetter.com</p>\
\
<h3 class="showhide_heading">Mac Setup</h3>\
\
<ul><li><a class="wiki" href="tiki-index.php?page=Setup+a+New+Mac+for+Astronomy">Setup Guide</a> for Mac Astronomers</li>\
	<li><a class="wiki" href="tiki-index.php?page=Mac+Apps">Mac Apps</a> - Top apps for boosting astronomy productivity</li>\
	<li><a class="wiki" href="tiki-index.php?page=Mac+Care">Mac Care and Maintenance</a> - Advice for keeping your Mac operating well.</li>\
	<li><a class="wiki" href="tiki-index.php?page=iPhone+OS+Apps">iPhone and iPad Apps</a> - <a class="wiki" href="http://www.astrobetter.com/tag/iphone/">related blog posts</a>\
	<ul><li><a class="wiki" href="tiki-index.php?page=Android+Apps">Android Apps</a></li>\
	</ul></li>\
	<li><a class="wiki" href="tiki-index.php?page=Setup+User+Accounts">Setup User Accounts</a> - For those who integrate into a larger network (beyond just ssh and such)</li>\
	<li><a class="wiki" href="tiki-index.php?page=scisoft">Scisoft</a> - quick way to install many data reduction packages</li>\
	<li><a class="wiki" href="tiki-index.php?page=windows">Running Windows on OS X</a></li>\
	<li><a class="wiki" href="tiki-index.php?page=Computing">Computing</a> - Other useful computing resources.</li>\
</ul><h3>Tips and Tricks (by application)</h3>\
\
<ul><li><a class="wiki" href="astro-comp-ed">Computing</a> - compilation of tutorials and activities for teaching/learning</li>\
	<li><a class="wiki" href="tiki-index.php?page=idl">IDL</a> - Installation Tips and Common IDL problems</li>\
	<li><a class="wiki" href="tiki-index.php?page=python">Python</a> - see also <a class="wiki" href="http://www.astrobetter.com/category/python/">related blog posts</a>\
	<ul><li><a class="wiki" href="tiki-index.php?page=Python+Setup+for+Astronomy">Setting up Python for Astronomy</a>. There are several ways to do this.</li>\
		<li><a class="wiki" href="tiki-index.php?page=pyraf">PyRAF</a></li>\
		<li><a class="wiki" href="tiki-index.php?page=idl_vs_python">IDL vs. Python</a> pros and cons</li>\
		<li><a class="wiki" href="tiki-index.php?page=Python+Switchers+Guide">Python Switchers Guide</a> (i.e. Python translations of IDL and IRAF commands)</li>\
	</ul></li>\
	<li><a class="wiki" href="tiki-index.php?page=AIPS">AIPS/CASA</a> - radio/sub-mm interferometric data reduction</li>\
	<li><a class="wiki" href="tiki-index.php?page=LaTeX">LaTeX</a> - <a class="wiki" href="http://www.astrobetter.com/tag/latex/">related blog posts</a></li>\
	<li><a class="wiki" href="tiki-index.php?page=sshfs">Mounting remote directories (SSHFS</a>)</li>\
	<li><a class="wiki" href="tiki-index.php?page=osx">OS X</a> - general tips</li>\
	<li><a class="wiki" href="tiki-index.php?page=pgplot">PGPLOT</a></li>\
	<li><a href="http://www.astrobetter.com/wiki/tiki-index.php?page=DAOphot">DAOphot</a></li>\
	<li><a class="wiki" href="tiki-index.php?page=MATLAB">MATLAB</a> - packages and tools for astronomy</li>\
	<li><a href="http://www.stsci.edu/science/starburst99/docs/default.htm">Starburst 99</a> (spectrophotometric simulation of star-forming galaxies)</li>\
</ul><h3>Astronomical Methods</h3>\
\
<ul><li><a class="wiki" href="tiki-index.php?page=Observing">Observing</a> - info for various telescopes and instruments\
\
	<ul><li><a class="wiki" href="tiki-index.php?page=Airmass+and+Visibility+Plots">Airmass and Visibility Plots</a></li>\
	</ul></li>\
	<li><a class="wiki" href="tiki-index.php?page=How+to+observe">How to observe</a> - general advice for the new observer</li>\
	<li><a class="wiki" href="tiki-index.php?page=Data+Reduction">Data Reduction</a></li>\
	<li><a class="wiki" href="tiki-index.php?page=Making+Images">Making Images</a> - IDL, SuperMongo, etc.</li>\
	<li><a class="wiki" href="tiki-index.php?page=Analysis+Tools">Analysis Tools</a> - <a class="wiki" href="http://www.astrobetter.com/category/analysis/">blog posts</a></li>\
	<li><a class="wiki" href="tiki-index.php?page=Data+Modeling">Data Modeling</a></li>\
	<li><a class="wiki" href="tiki-index.php?page=Statistical+Tools">Statistical Tools</a></li>\
	<li><a class="wiki" href="tiki-index.php?page=Simulations">Simulations</a></li>\
	<li><a class="wiki" href="tiki-index.php?page=Astronomical+Databases">Astronomical Databases</a> - Individually maintained web pages that provide data and/or catalogs.</li>\
</ul><p><a id="career"></a></p>\
\
\
</ul><h3>Other Resources</h3>\
\
<ul><li><a class="wiki" href="tiki-index.php?page=Getting+Started+Guide" title="Getting Started Guide">Getting Started Guide</a> - Guide for those just getting started in Astronomy.</li>\
	<li><a class="wiki" href="tiki-index.php?page=Astro-ph+Tools">Astro-ph Tools</a></li>\
	<li><a class="wiki" href="tiki-index.php?page=Telescope+and+Grant+Proposal+Deadline+Calendar" title="Telescope and Grant Proposal Deadline Calendar">Telescope and Grant Proposal Deadline Calendar</a></li>\
	<li><a class="wiki" href="tiki-index.php?page=Writing">Writing</a> - Resources for writing papers and proposals.</li>\
	<li><a class="wiki" href="tiki-index.php?page=Refereeing+and+Peer+Review" title="Refereeing and Peer Review">Refereeing and Peer Review</a> - Thoughts on writing referee reports.</li>\
	<li><a class="wiki" href="tiki-index.php?page=Presentation+Skills">Presentation Skills</a> - Tips for giving talks and posters.</li>\
	<li><a href="http://www.astrobetter.com/wiki/tiki-index.php?page=Mental+Health">Mental Health</a> - Links to articles about academia and mental health</li>\
	<li><a class="wiki" href="tiki-index.php?page=Diversity">Diversity</a> - Links to articles relevant to fostering diversity in physics and astronomy.</li>\
	<li><a class="wiki" href="tiki-index.php?page=Acknowledgements">Acknowledgements</a> - How to acknowledge (in paper, talks) the various institutions that support your research.</li>\
</ul>"')
    ob.save()
    u=User.objects.get_or_create(username="admin")
    if(u[1]==True):
        u[0].save()#If the user is not present ,create it
    ob.authors.add(u[0])
    ob.tags.add("home")

"""
Main population script that parses JSON and stores them in model objects and then to the database
"""
def populate(path_localdata,obj):
    author=""
    title=""
    desc=""
    date=""
    s=""
    typeObj=type(obj)#Find which type of model we are populating
    no=len(os.walk(path_localdata).next()[2])#find no. of json files in the directory
    for i in range(1,no+1):
        try:
            with open(path_localdata+"//"+str(i)+".json") as data_file:#open the json file
                try:
                    data=json.load(data_file)#load data in python variable
                except:
                    print data_file
                    continue
                t=typeObj()#create a new object
                for name in data:
                    if (name=='tags'):
                        pass
                        """
                            for items in data[name]:
                                s1=str(items)
                                t.tags.add(s1)#Add tags one by one.Note that this handles duplicate tags automatically
                        """
                    else:
                        s=data[name]#Find the field
                        if(name=='author'):
                            author=s
                        elif(name=='title'):
                            title=s
                        elif(name=='description'):
                            desc=s
                        elif(name=='date_published'):
                            date=s
                t.title=title#Set the title
                if type(obj)==Package:
                    try:
                        p1=desc.index('Description')
                        p_end=desc.index('<br/>',p1)
                        p_temp=desc.index('Homepage URL:')
                        p2=desc.index('>',p_temp)
                        p2=p2+1
                        p2_end=desc.index('</a>',p2)
                        t.abstract=desc[p1+12:p_end]
                        t.homepage=desc[p2:p2_end]
                        temp=desc
                        desc=temp[:p1]+temp[p2_end+4:]
                    except:
                        print title
                t.body=desc#Add the body
                t.input_type="WYSIWYG"
                t.state="submitted"
                t.slug=slugify(title)+str(random.randrange(1,100+1))#If 2 objects have same title,this prevents the same slug from being generated
                try:
                    t.save()#Save the current state
                except:
                    continue
                t.published=datetime.datetime.strptime(date,"%Y-%m-%d") #Add publishing date
                u=User.objects.get_or_create(username=author)#If user is absent, create user
                t.save()
                if(u[1]==True):
                    u[0].save()#If the user is not present ,create it
                t.authors.add(u[0])
                t.save()#save all elements
                for name in data:
                    if (name=='tags'):
                            for items in data[name]:
                                s1=str(items)
                                t.tags.add(s1)#Add tags one by one.Note that this handles duplicate tags automatically
                print("Entered an element successfully!")
        except IOError:
            no=no+1
            continue
# Start execution here!
if __name__ == '__main__':
    _temp_orig_path=os.getcwd()
    _orig_path=os.path.dirname(_temp_orig_path)
    base=os.path.join(_orig_path,'ported_data/html')#Path to Json data
    opt=raw_input("Do you wish to initialize the database(create user organizations,home wiki page,etc):(y/n)")
    if opt=='y':
        initialize()
    #Take inputs
    print "Starting Astropython population script..."
    opt=raw_input("Do you want to populate all the sections? (y/n):")
    if opt=='y':
        populate(path_localdata=os.path.join(base,'Tutorials'),obj=Tutorial())
        populate(path_localdata=os.path.join(base,'Code Snippets'),obj=Snippet())
        populate(path_localdata=os.path.join(base,'Blogs'),obj=Blog())
        populate(path_localdata=os.path.join(base,'Resources and Tools'),obj=Package())
    else:
        opt=raw_input("Do you want to populate the tutorials? (y/n):")
        if opt=='y':
            obj=Tutorial()
            populate(path_localdata=os.path.join(base,'Tutorials'),obj=obj)
        opt=raw_input("Do you want to populate the code snippets? (y/n):")
        if opt=='y':
            obj=Snippet()
            populate(path_localdata=os.path.join(base,'Code Snippets'),obj=obj)
        opt=raw_input("Do you want to populate the blogs? (y/n):")
        if opt=='y':
            obj=Blog()
            populate(path_localdata=os.path.join(base,'Blogs'),obj=obj)
        opt=raw_input("Do you want to populate the packages? (y/n):")
        if opt=='y':
            obj=Package()
            populate(path_localdata=os.path.join(base,'Resources and Tools'),obj=obj)