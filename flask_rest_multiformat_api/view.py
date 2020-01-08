# -*- coding: utf-8 -*-

from flask import (abort, request, make_response)
from flask.views import MethodView
from .serialize import serialise, apply_data_to_model
from .utils import build_filter, loads_filters
from .queries import get_single, get_many
import json
from werkzeug.exceptions import BadRequest, MethodNotAllowed
from marshmallow import ValidationError
from sqlalchemy.orm import Query
from .format import DATA_FORMATER
from .exceptions import ApiException
from flask_rest_multiformat_api.errors import (ApiError, ObjectNotFoundError,
                                               InvalidDataError
                                                )

DEFAULT_FORMATER = DATA_FORMATER['jsonapi']


class BaseView(MethodView):
    model = None
    session = None
    allowed_methods = ['GET', 'POST', 'PATCH', 'PUT', 'DELETE']
    type = ''
    links = {}
    data_format = "jsonapi"
    handle_exception = (ValidationError)
    _decorators = {}

    def __init__(self, *args, **kwargs):
        super(MethodView, self).__init__(*args, **kwargs)
        allowed_method = [method.lower() for method in self.allowed_methods]
        methods = [meth.lower() for meth in self.methods]

        self.data_formater = DATA_FORMATER.get(self.data_format,
                                               DEFAULT_FORMATER
                                               )

        for method in methods:
            if method not in allowed_method:
                setattr(self, method, None)

    def apply_decorators(self, meth):
        decorators = self._decorators.get(request.method.lower(), [])
        for decorator in decorators:
            meth = decorator(meth)
        return meth

    def dispatch_request(self, *args, **kwargs):
        meth = getattr(self, request.method.lower(), None)
        print('meth :', meth)
#         print('methodes: ', lower_methods,request.method.lower() )
        # If the request method is HEAD and we don't have a handler for it
        # retry with GET.
        if meth is None and request.method == 'HEAD':
            meth = getattr(self, 'get', None)

        if meth is None:
            raise MethodNotAllowed('%s method not allowed.' %
                                   request.method.lower()
                                   )
        assert meth is not None, 'Unimplemented method %r' % request.method
        try:
            meth = self.apply_decorators(meth)
            return meth(*args, **kwargs)
        except (ApiException, ValidationError) as e:
            if isinstance(e, ValidationError):
                errors = [InvalidDataError(e.messages)]
                return self.data_formater.build_error_response(errors)
            return self.data_formater.build_error_response(e.errors)


class ModelDetailView(BaseView):
    allowed_methods = ['GET', 'PUT', 'PATCH', 'DELETE']
    
    def get_object(self, *args, **kwargs):
        id = kwargs.get("id")
        model_object = get_single(self.session, self.model, id)
        return model_object

    def get(self, *args, **kwargs):
        print(args, kwargs)
        orm_obj = self.get_object(*args, **kwargs)
        if not orm_obj:
            error = ObjectNotFoundError(self.model, kwargs.get("id"))
            raise ApiException([error], 404)
        orm_obj_json = serialise(orm_obj, self)
        return self.data_formater.create_response(orm_obj_json, 200)

    def update(self, *args, **kwargs):
        code = 201
        model_obj = self.get_object(*args, **kwargs)
        print("MODEL OBJ: ", model_obj)
        if model_obj is None:
            error = ObjectNotFoundError(self.model, kwargs.get("id"))
            raise ApiException([error], 404)
        data = self.data_formater.parse_data(request.data)
        model_obj = apply_data_to_model(self.model, model_obj, data) if \
                    isinstance(data, dict) else data
        if not model_obj.id:
            self.session.add(model_obj)
        self.session.commit()
        response = serialise(model_obj, self)
        return self.data_formater.create_response(response, code)

    def delete(self, *args, **kwargs):
        orm_obj = self.get_object(*args, **kwargs)
        if not orm_obj:
            error = ObjectNotFoundError(self.model, kwargs.get("id"))
            raise ApiException([error], 404)
        self.session.delete(orm_obj)
        self.session.commit()
        return '', 202

    def put(self, *args, **kwargs):
        return self.update(*args, **kwargs)

    def patch(self, *args, **kwargs):
        return self.update(*args, **kwargs)


class ModelListView(BaseView):
    allowed_methods = ['GET', 'POST']

    def get_objects(self, *args, **kwargs):
        filters_dict = loads_filters(request)
        order = request.args.get('sort', '')
        order_by = request.args.get('sort_by', '')
        number_par_page = request.args.get('per_page', 50)
        page_number = request.args.get('page', 0)
        model_objects = get_many(self.session, self.model,
                                 filters_dict, order_by, order,
                                 number_par_page, page_number
                                 )
        return model_objects

    def get(self, *args, **kwargs):
        orm_objs = self.get_objects(*args, **kwargs)
        page_number = request.args.get('page', 0)
        orm_objs_json = serialise(orm_objs, self,
                                  page_number=page_number,
                                  )
        return orm_objs_json, 200

    def post(self, *args, **kwargs):
        code = 201
        data = self.data_formater.parse_data(request.data) 
        self.before_post(args, kwargs, data)
        model_obj = self.create_object(data, *args, **kwargs)
        self.after_create_object(model_obj, *args, **kwargs)
        response = serialise(model_obj, self)
        self.after_post(model_obj, args, kwargs)
        return response, code

    def create_object(self, data, *args, **kwargs):
        model_obj = self.schema().load(data, partial=True)
        self.session.add(model_obj)
        self.session.commit()
        return model_obj
        
    def after_create_object(self, new_object, *args, **kwargs):
        pass
        
    def before_post(self, args, kwargs, data=None):
        pass

    def after_post(self, new_object, args, kwargs):
        pass


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

        self.data_formater = DATA_FORMATER.get(self.data_format, DEFAULT_FORMATER)

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
        relation_objects = related_object.all() if \
                           isinstance(related_object, Query)\
                           else related_object
        relation_model = relation_objects.__class__ if not isinstance(relation_objects, list) \
                         else  relation_objects[0].__class__
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
        relation_obj = query_function(self.session, relation_model, id_relation)
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
        relation_obj = query_function(self.session, relation_model, id_relation)
        if not relation_obj:
            return 'Object for relation not found', 400
        relation_objects.remove(relation_obj)
        self.session.commit()
        return '', 201
