import json
from flask import request, MethodView
from sqlalchemy.orm import Query
from .base import BaseView
from ..queries import get_single, get_many
from ..serialize import serialise

from ..format import DATA_FORMATER

DEFAULT_FORMATER = DATA_FORMATER['jsonapi']


class RelationshipView(BaseView):
    model = None
    session = None
    relation_attribute_name = ''
    queries = {'single': get_single}
    methods = ['GET', 'POST', 'DELETE']
    allowed_methods = ['GET', 'POST', 'DELETE']
    data_format = "jsonapi"

    def __init__(self, *args, **kwargs):
        super(MethodView, self).__init__(*args, **kwargs)
        allowed_method = [method.lower() for method in self.allowed_methods]
        methods = [meth.lower() for meth in self.methods]

        self.data_formater = DATA_FORMATER.get(self.data_format,
                                               DEFAULT_FORMATER)

        for method in methods:
            if method not in allowed_method:
                setattr(self, method, None)

    def get_object(self, *args, **kwargs):
        id = kwargs.get("id")
        model_object = get_single(self.session, self.model, id)
        return model_object

    def get_related_object(self, orm_obj):
        relation_object = getattr(orm_obj, self.relation_attribute_name, None)
        return relation_object

    def get(self, *args, **kwargs):
        orm_object = self.get_object(*args, **kwargs)
        related_object = self.get_related_object(orm_object)
        # to do: add filter for performance
        relation_objects = related_object.all() if isinstance(
            related_object, Query) else related_object
        relation_model = relation_objects.__class__ if not isinstance(
            relation_objects, list) else relation_objects[0].__class__
        id_relation = kwargs.get("id_relation")
        if id_relation:
            object = None
            if relation_objects:
                for relation_object in relation_objects:
                    if relation_object.id == id_relation:
                        object_str = serialise(relation_object, self)
        else:
            object_str = serialise(relation_objects, self)
        return object_str, 200

    def post(self, id):
        print("post request")
        data = json.loads(request.data)
        id_relation = data.get('id', None)
        if not id_relation:
            return 'Id relation must be specified', 400

        query_function = self.queries['single']
        orm_obj = query_function(self.session, self.model, id)
        relation_objects = getattr(orm_obj, self.relation_attribute_name, [])

        model_attr = getattr(self.model, self.relation_attribute_name, None)
        relation_model = model_attr.property.mapper.class_
        relation_obj = query_function(self.session, relation_model,
                                      id_relation)
        if not relation_obj:
            return 'Object for relation not found', 400

        relation_objects.append(relation_obj)
        self.session.commit()

        object_str = serialise(relation_obj, self)
        return object_str, 201

    def delete(self, id, id_relation):
        print("delete request")
        query_function = self.queries['single']
        orm_obj = query_function(self.session, self.model, id)
        relation_objects = getattr(orm_obj, self.relation_attribute_name, [])

        model_attr = getattr(self.model, self.relation_attribute_name, None)
        relation_model = model_attr.property.mapper.class_
        relation_obj = query_function(self.session, relation_model,
                                      id_relation)
        if not relation_obj:
            return 'Object for relation not found', 400
        relation_objects.remove(relation_obj)
        self.session.commit()
        return '', 201
