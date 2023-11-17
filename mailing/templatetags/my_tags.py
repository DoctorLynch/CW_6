from django import template
from django.conf import settings

register = template.Library()


@register.filter
def media_url(value):
    media_root = settings.MEDIA_URL
    return f"{media_root}{value}"


@register.simple_tag()
def mediafile(value):
    return f'/media/{value}'
