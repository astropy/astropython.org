from django import template
from markdown import markdown
import re
from main.utilities import get_section

register = template.Library()

def raw_content(value):
    value=markdown(value)
    plain_content=re.sub('<[^<]+?>', '', value)
    plain_content.replace("&gt;", ">")
    plain_content.replace("&lt;", "<")
    return plain_content


def get_section(value):
    return value.__class__.__name__

def isEven(value,arg):
    if arg.index(value)%2==0:
        return True
    return False

def sort_tags(queryset):
    t=[]
    for q in queryset:
        t.append(q.name)
    t= sorted(t, key=lambda s: s.lower())
    return t

register.filter('isEven',isEven)
register.filter('get_section',get_section)
register.filter('raw_content', raw_content)
register.filter('sort_tags', sort_tags)
