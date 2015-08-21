from django.db.models.signals import post_save,post_init
from django.dispatch import receiver
from django.contrib.auth.models import User,Group
from moderation import signals
from django.core.mail import send_mail

@receiver(signals.post_moderation,dispatch_uid="moderation_approval")
def moderation_approval(sender,instance,status,**kwargs):
    if instance.state=="submitted":
        print "enteeeeeeeeering"
        try:
            print "enteeeeeeeeering2"
            if status==1:
                print "enteeeeeeeeering4"
                subject="AstroPython Post Approved !"
                message="Your post at AstroPython is approved"
                html_m='<hr /><h2 style="text-align:center"><code><tt><span style="font-family:trebuchet ms,helvetica,sans-serif"><strong>AstroPython - Python for Astronomers</strong></span></tt></code></h2><hr /><p>Your Post "'+instance.title+'"&nbsp;&nbsp;has&nbsp;been approved by the Moderators !</p><p>Access it <a href="http://astropython.org'+instance.get_absolute_url()+'">here</a> !</p><p>Thank you,</p><p><strong>AstroPython Team</strong></p><hr /><p style="text-align:right"><span style="font-size:10px">Currently , you cannot unsubscribe to these emails</span></p>'
            elif status==0:
                print "enteeeeeeeeering5"
                subject="AstroPython Post Rejected !"
                message="Your post at AstroPython has been rejected"
                html_m='<hr /><h2 style="text-align:center"><code><tt><span style="font-family:trebuchet ms,helvetica,sans-serif"><strong>AstroPython - Python for Astronomers</strong></span></tt></code></h2><hr /><p>Your Post "'+instance.title+'"&nbsp;&nbsp;has&nbsp;been rejected by the Moderators ! Reach us through our footer feedback form on www.astropython.org </p><p>Thank you,</p><p><strong>AstroPython Team</strong></p><hr /><p style="text-align:right"><span style="font-size:10px">Currently , you cannot unsubscribe to these emails</span></p>'
            print "enteeeeeeeeering3"
            from_email="notifications@astropython.org"
            send_mail(subject,message,from_email,[str(user.email) for user in instance.authors.all()], fail_silently=False,html_message=html_m)
        except:
            print "No Email Provided"