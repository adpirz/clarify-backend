import re
from django.utils import timezone

from django.db import models
from django.utils import timezone


def camel_to_underscore(name):
    """
    See here: http://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case

    >>> camel_to_underscore('CamelCase')
    'camel_case'
    >>> camel_to_underscore('CamelCamelCase')
    'camel_camel_case'
    >>> camel_to_underscore('Camel2Camel2Case')
    'camel2_camel2_case'
    >>> camel_to_underscore('getHTTPResponseCode')
    'get_http_response_code'
    >>> camel_to_underscore('get2HTTPResponseCode')
    'get2_http_response_code'
    >>> camel_to_underscore('HTTPResponseCode')
    'http_response_code'
    >>> camel_to_underscore('HTTPResponseCodeXYZ')
    'http_response_code_xyz'

    """

    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def get_academic_year(date=None):
    today = date or timezone.now().date()
    return today.year if today.month < 7 else today.year + 1


def SourceObjectForeignKey(fk_model, **kwargs):
    return models.ForeignKey(fk_model, to_field='source_object_id', **kwargs)
