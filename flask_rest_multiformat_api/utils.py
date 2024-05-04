# -*- coding: utf-8 -*-

from sqlalchemy import inspect as inspect_db
from sqlalchemy.orm import relationships, properties
import inspect
import json
import datetime
from .log import logger


def get_attr_names(model):
    return inspect_db(model).columns.keys()


def get_relationships_models(model):
    relationships = inspect_db(model).relationships
    models = [re.mapper.class_ for re in relationships]
    return models


def build_filter(request, model):
    filter = {}
    model_attr_names = get_attr_names(model)
    for key, value in request.args.items():
        if key not in model_attr_names:
            raise ValueError('%s is not a valid parameter' % key)
        filter[key] = value
    return filter


def get_primary_key_name(model):
    return inspect_db(model).primary_key[0].name


def is_valid_filter(filter):
    is_valid = 'name' in filter and 'op' in filter and 'val' in filter
    return is_valid


def validate_filters(filters):
    for filter in filters:
        if not is_valid_filter(filter):
            return False
    return True


def loads_filters(request):
    filter_dict = []
    filters = request.args.get('filters', None)
    logger.info(f"filters: {filters}")
    if filters and isinstance(filters, str):
        filter_dict = json.loads(filters)
    return filter_dict


def keep_colum_relationship(model, attr_names):
    new_attr_names = []
    for attr_name in attr_names:
        model_attr = getattr(model, attr_name, None)
        if not hasattr(model_attr, 'property'):
            continue
        if isinstance(model_attr.property,
                      relationships.RelationshipProperty) or isinstance(
                          model_attr.property, properties.ColumnProperty):
            new_attr_names.append(attr_name)
    return new_attr_names


def get_class_atributes(model):
    exclude_attr = ['metadata', 'query', 'query_class']
    attributes = [i for i in dir(model) if not callable(i)]
    attributes = [
        a for a in attributes if not (a.startswith('__') and a.endswith('__'))
    ]
    attributes = [
        a for a in attributes
        if not (a.startswith('_sa_')) and not a.startswith('_decl_')
    ]
    attributes = [a for a in attributes if a not in exclude_attr]
    attributes = keep_colum_relationship(model, attributes)
    return attributes
