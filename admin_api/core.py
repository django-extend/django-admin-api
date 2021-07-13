from django.db import models
from django.db.models.options import Options
from django.utils.text import capfirst
from django.core.exceptions import FieldDoesNotExist

class ModelInfo:
    app_name = None
    app_label = None
    model_name = None
    model_label = None
    prefix = None

def parse_model(model: models.Model) -> ModelInfo:
    meta: Options = model._meta
    rs = ModelInfo
    rs.app_name = meta.app_config.label.lower()
    rs.app_label = meta.app_config.verbose_name
    rs.model_name = meta.model_name.lower()
    rs.model_label = meta.verbose_name
    rs.prefix = f'resource/{rs.app_name}/{rs.model_name}'
    return rs


def get_short_description(obj, attr_name):
    attr = getattr(obj, attr_name)
    if hasattr(attr, 'short_description'):
        return getattr(attr, 'short_description')
    else:
        return capfirst(attr.replace('_', ' '))

def is_model_field(admin, name):
    try:
        admin.opts.get_field(name)
        return True
    except FieldDoesNotExist:
        return False

def has_model_attr(admin, name):
    if is_model_field(admin, name):
        return False
    return hasattr(admin.model, name)

def get_model_field_or_attr_name(admin, name):
    try:
        return admin.opts.get_field(name).verbose_name
    except FieldDoesNotExist:
        if hasattr(admin.model, name):
            return get_short_description(admin.model, name)

def get_field_title(admin, field):
    if field == '__str__':
        return admin.model._meta.verbose_name
    title = get_model_field_or_attr_name(admin, field)
    if title:
        return title
    return get_short_description(admin, field)

def get_passwords(admin):
    rs = {}
    for name, funcname in admin.passwords:
        rs[name] = funcname
    return rs
