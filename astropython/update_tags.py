import os,json


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'astropython.settings')

#Setup Django and add all dependencies and code automatically
import django
django.setup()


from django.contrib.auth.models import User,Group

from main.models import *
from taggit.models import Tag,TaggedItem

def get_or_create_dirs(path_data):
    if not os.path.exists(path_data):
        os.makedirs(path_data)
    return path_data


def backup(path_localdata,model):
    tag_list=model.tags.all()
    for item in tag_list:
        tagged=TaggedItem.objects.filter(tag=item)
        print tagged
    """
    for obj in obj_list:
        if not (model == User or model == Feed or model==Contact):
            address=(path_localdata+'\\'+(obj.slug)+".json")
        elif model==User:
            address=(path_localdata+'\\'+(obj.username)+".json")
        elif model==Feed:
            address=(path_localdata+'\\'+(obj.title)+".json")
        elif model==Contact:
            address=(path_localdata+'\\'+(obj.username)+".json")
        with open(address,"w") as outfile:
            if (model==Tutorial or model==Snippet or model==Wiki or model==Announcement or model==News or model==Blog):
                json.dump({'title':obj.title,'slug':obj.slug,'abstract':obj.abstract,'input_type':obj.input_type,'body':(obj.body).encode('utf-8').strip(),'author':[user.username for user in obj.authors.all()],'state':obj.state,'created':str(obj.created),'tags':[tag_name.name for tag_name in obj.tags.all()]},outfile)
            elif model== Package:
                json.dump({'title':obj.title,'slug':obj.slug,'abstract':obj.abstract,'input_type':obj.input_type,'body':(obj.body).encode('utf-8').strip(),'author':[user.username for user in obj.authors.all()],'state':obj.state,'created':str(obj.created),'tags':[tag_name.name for tag_name in obj.tags.all()],'category':obj.category,'homepage':obj.homepage,'docs':obj.docs},outfile)
            elif model== EducationalResource:
                json.dump({'title':obj.title,'slug':obj.slug,'abstract':obj.abstract,'input_type':obj.input_type,'body':(obj.body).encode('utf-8').strip(),'author':[user.username for user in obj.authors.all()],'state':obj.state,'created':str(obj.created),'tags':[tag_name.name for tag_name in obj.tags.all()],'start_date':str(obj.start_date),'website':obj.website,'instructor_names':obj.instructor_names,'contents':obj.contents,'background':obj.background,'faq':obj.faq,'language':obj.language},outfile)
            elif model==Event:
                json.dump({'title':obj.title,'slug':obj.slug,'input_type':obj.input_type,'body':(obj.body).encode('utf-8').strip(),'author':[user.username for user in obj.authors.all()],'state':obj.state,'created':str(obj.created),'tags':[tag_name.name for tag_name in obj.tags.all()],'location':obj.location,'website':obj.website,'start_date_time':str(obj.start_date_time),'end_date_time':str(obj.end_date_time),'all_day_event':str(obj.all_day_event)},outfile)
            elif model==Contact:
                json.dump({'username':obj.username,'email':obj.email,'content':obj.content},outfile)
            elif model==Feed:
                json.dump({'title':obj.title,'url':obj.url,'section':obj.section,'notes':obj.notes},outfile)
            elif model==User:
                json.dump({'username':obj.username,'email':obj.email,'first_name':obj.first_name,'last_name':obj.last_name},outfile)
"""


if __name__ == '__main__':
    _temp_orig_path=os.getcwd()
    _orig_path=os.path.dirname(_temp_orig_path)
    base=get_or_create_dirs(os.path.join(_orig_path,'backup'))#Path to Json data
    print "Starting Backup Script..."
    print "\nStep 1/12: Backing up Announcements..."
    backup(path_localdata=get_or_create_dirs(path_data=os.path.join(base,'Announcements')),model=Announcement)
    print "\nStep 2/12: Backing up Blogs..."
    backup(path_localdata=get_or_create_dirs(path_data=os.path.join(base,'Blogs')),model=Blog)
    print "\nStep 3/12: Backing up Feedbacks..."
    backup(path_localdata=get_or_create_dirs(path_data=os.path.join(base,'Feedbacks')),model=Contact)
    print "\nStep 4/12: Backing up Education Resources..."
    backup(path_localdata=get_or_create_dirs(path_data=os.path.join(base,'Educational Resources')),model=EducationalResource)
    print "\nStep 5/12: Backing up Events..."
    backup(path_localdata=get_or_create_dirs(path_data=os.path.join(base,'Events')),model=Event)
    print "\nStep 6/12: Backing up Feeds...."
    backup(path_localdata=get_or_create_dirs(path_data=os.path.join(base,'Feed')),model=Feed)
    print "\nStep 7/12: Backing up News..."
    backup(path_localdata=get_or_create_dirs(path_data=os.path.join(base,'News')),model=News)
    print "\nStep 8/12: Backing up Packages..."
    backup(path_localdata=get_or_create_dirs(path_data=os.path.join(base,'Packages')),model=Package)
    print "\nStep 9/12: Backing up Snippets..."
    backup(path_localdata=get_or_create_dirs(path_data=os.path.join(base,'Snippets')),model=Snippet)
    print "\nStep 10/12: Backing up Tutorials..."
    backup(path_localdata=get_or_create_dirs(path_data=os.path.join(base,'Tutorials')),model=Tutorial)
    print "\nStep 11/12: Backing up Wiki..."
    backup(path_localdata=get_or_create_dirs(path_data=os.path.join(base,'Wiki')),model=Wiki)
    print "\nStep 12/12: Backing up User data..."
    backup(path_localdata=get_or_create_dirs(path_data=os.path.join(base,'Users')),model=User)
    print "\nBackup Complete! Commit the files on Github to complete backup !"