# -*- coding: utf-8 -*-

from .utils import get_attr_names, get_class_atributes
from .date_util import date_to_str_fr
import datetime
from sqlalchemy.orm import relationships
from .format import DATA_FORMATER


DEFAULT_FORMATER = DATA_FORMATER['jsonapi']

RESULT_BASE_DICT = {
    'data': [],
    }


def object_to_dict(object, model, with_info=False, additional_columns=[], exclude_culumn=[]):
    if not object:
        return {}
    dict = {}
    for attr_name in get_attr_names(model):
        if attr_name in exclude_culumn:
            continue
        dict[attr_name] = getattr(object, attr_name)
        if isinstance(dict[attr_name], datetime.datetime):
            dict[attr_name] = date_to_str_fr(dict[attr_name])
    if with_info and additional_columns:
        for col in additional_columns:
            dict[col] = getattr(object, col)
    return dict


def get_relationship_dict(orm_obj, attr_name, relationship_class):
    relationship_dicts = []
    obj_attr = getattr(orm_obj, attr_name, None)
    if isinstance(obj_attr, list):
        for obj in obj_attr:
            obj_dict = object_to_dict(obj, relationship_class)
            relationship_dicts.append(obj_dict)
    else:
        relationship_dicts = object_to_dict(obj_attr, relationship_class)
    return relationship_dicts

    
def add_relationships(object_dict, orm_obj, model, exclude_culumn=[]):
    attributes = get_class_atributes(model)
    for attr_name in attributes:
        if attr_name in exclude_culumn:
            continue 
        model_attr = getattr(model, attr_name, None)
        if isinstance(model_attr.property, relationships.RelationshipProperty):
            relation_class = model_attr.property.mapper.class_
            relationship_dicts = get_relationship_dict(orm_obj, attr_name, relation_class)
            object_dict[attr_name] = relationship_dicts
    return object_dict


def apply_data_to_model(model, model_obj, data):
    for key, value in data.items():
        model_attr = getattr(model, key, None)
        if model_attr:
            setattr(model_obj, key, value) 
    return model_obj



def build_dict_response(orm_obj__dict, data_formater, page_number, **kwargs):
    result_dict = RESULT_BASE_DICT
    result_dict['data'] = data_formater.build_data_dict(orm_obj__dict, **kwargs)
    if isinstance(orm_obj__dict, list):
        result_dict['count'] = len(orm_obj__dict)
        result_dict['page'] = page_number
    return result_dict


def serialise(orm_obj, view, page_number=0):
    Schema = view.schema
    model_schema = Schema(many=True) if isinstance(orm_obj, list) else Schema() 
    orm_obj__dict = model_schema.dump(orm_obj)
    data_formater = view.data_formater
    kwargs = {
                "type": view.type,
                "links": view.links
            }
    result_dict = build_dict_response(orm_obj__dict, data_formater, page_number, **kwargs)
    formated_response = data_formater.format_response(result_dict)
    return formated_response


def deserialise(data, model):
    new_model_obj = model()
    for attr_name in get_attr_names(model):
        setattr(new_model_obj, attr_name, data.get(attr_name)) 
    return new_model_obj
    
