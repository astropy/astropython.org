import os,json


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'astropython.settings')

#Setup Django and add all dependencies and code automatically
import django
django.setup()


from django.contrib.auth.models import User,Group

from main.models import *

def get_or_create_dirs(path_data):
    if not os.path.exists(path_data):
        os.makedirs(path_data)
    return path_data

def initialize():

    Group.objects.get_or_create(name="Trusted Users")
    Group.objects.get_or_create(name="Preview Users")
    Group.objects.get_or_create(name="Banned Users")
    User.objects.create_superuser(username="admin",password="admin",email="test@example.com")


def restore(path_localdata,model):
    for root, dirs, files in os.walk(path_localdata):
        for file in files:
            if file.endswith(".json"):
                with open(os.path.join(root, file)) as data_file:#open the json file
                    data=json.load(data_file)#load data in python variable
                    if model==User or model==Contact or model==Feed:
                        m=model(**data)
                        m.save()
                    else:
                        authors=data['author'][0]
                        tags=data['tags']
                        data.pop("tags",None)
                        data.pop("author",None)
                        m=model(**data)
                        m.save()
                        u=User.objects.get_or_create(username=authors)
                        if(u[1]==True):
                            u[0].save()#If the user is not present ,create it
                        m.authors.add(u[0])
                        #m.published=data['published']
                        m.save()#save all elements
                        for items in tags:
                            s1=str(items)
                            m.tags.add(s1)#Add tags one by one.Note that this handles duplicate tags automatically


if __name__ == '__main__':
    _temp_orig_path=os.getcwd()
    _orig_path=os.path.dirname(_temp_orig_path)
    base=get_or_create_dirs(os.path.join(_orig_path,'backup'))#Path to Json data
    print "Starting Restore Script..."
    opt=raw_input("Do you wish to initialize the database?:(y/n)")
    if opt=='y':
        initialize()

    print "\nStep 1/12: Restoring User data..."
    #restore(path_localdata=get_or_create_dirs(path_data=os.path.join(base,'Users')),model=User)
    print "\nStep 2/12: Restoring Announcements..."
    restore(path_localdata=get_or_create_dirs(path_data=os.path.join(base,'Announcements')),model=Announcement)
    print "\nStep 3/12: Restoring Blogs..."
    restore(path_localdata=get_or_create_dirs(path_data=os.path.join(base,'Blogs')),model=Blog)
    print "\nStep 4/12: Restoring Feedbacks..."
    restore(path_localdata=get_or_create_dirs(path_data=os.path.join(base,'Feedbacks')),model=Contact)
    print "\nStep 5/12: Restoring Education Resources..."
    restore(path_localdata=get_or_create_dirs(path_data=os.path.join(base,'Educational Resources')),model=EducationalResource)
    print "\nStep 6/12: Restoring Events..."
    restore(path_localdata=get_or_create_dirs(path_data=os.path.join(base,'Events')),model=Event)
    print "\nStep 7/12: Restoring Feeds...."
    restore(path_localdata=get_or_create_dirs(path_data=os.path.join(base,'Feed')),model=Feed)
    print "\nStep 8/12: Restoring News..."
    restore(path_localdata=get_or_create_dirs(path_data=os.path.join(base,'News')),model=News)
    print "\nStep 9/12: Restoring Packages..."
    restore(path_localdata=get_or_create_dirs(path_data=os.path.join(base,'Packages')),model=Package)
    print "\nStep 10/12: Restoring Snippets..."
    restore(path_localdata=get_or_create_dirs(path_data=os.path.join(base,'Snippets')),model=Snippet)
    print "\nStep 11/12: Restoring Tutorials..."
    restore(path_localdata=get_or_create_dirs(path_data=os.path.join(base,'Tutorials')),model=Tutorial)
    print "\nStep 11/12: Restoring Wiki..."
    restore(path_localdata=get_or_create_dirs(path_data=os.path.join(base,'Wiki')),model=Wiki)
    print "\n Restoration Complete!"