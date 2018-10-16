from django import template

register = template.Library()


def percentage(value):
    if not value:
        return ''
    return '{0:.2%}'.format(value)


register.filter('percentage', percentage)