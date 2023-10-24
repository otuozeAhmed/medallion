import re

from django.template import Library
from djf_surveys.utils import create_star as utils_create_star
register = Library()


@register.filter(name='addclass')
def addclass(field, class_attr):
    return field.as_widget(attrs={'class': class_attr})


@register.filter(name='get_id_field')
def get_id_field(field):
    parse = field.auto_id.split("_")
    return parse[-1]


@register.filter(name='create_star')
def create_star(number, args):
    return utils_create_star(active_star=int(number), id_element=args)

@register.filter(name='truncate_email')
def truncate_email(email):
    email = str(email)  
    pattern = r'^([^@]+)@.*$'
    match = re.match(pattern, email)
    
    if match:
        truncated_email = match.group(1)
        return truncated_email
    
    # Return the original email if it doesn't match the pattern
    return email
