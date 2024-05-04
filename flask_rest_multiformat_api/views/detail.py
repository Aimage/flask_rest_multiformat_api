from flask_rest_multiformat_api.exceptions import ApiException
from flask import request
from ..errors import ObjectNotFoundError
from .base import BaseView
from ..queries import get_single
from ..serialize import serialise, apply_data_to_model


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
        #         print("MODEL OBJ: ", model_obj)
        if model_obj is None:
            error = ObjectNotFoundError(self.model, kwargs.get("id"))
            raise ApiException([error], 404)

        model_obj = self.before_update_object(model_obj, *args, **kwargs)

        data = self.data_formater.parse_data(request.data)
        self.schema().validate(data, many=False, session=self.session)
        model_obj = apply_data_to_model(
            self.model, model_obj, data) if isinstance(data, dict) else data
        self.session.commit()
        response = serialise(model_obj, self)
        return self.data_formater.create_response(response, code)

    def delete(self, *args, **kwargs):
        orm_obj = self.get_object(*args, **kwargs)
        self.before_delete_object(orm_obj, *args, **kwargs)
        if not orm_obj:
            error = ObjectNotFoundError(self.model, kwargs.get("id"))
            raise ApiException([error], 404)
        self.session.delete(orm_obj)
        self.session.commit()
        self.after_delete_object(orm_obj, *args, **kwargs)
        return '', 202

    def put(self, *args, **kwargs):
        return self.update(*args, **kwargs)

    def patch(self, *args, **kwargs):
        return self.update(*args, **kwargs)

    def before_delete_object(self, orm_obj, *args, **kwargs):
        return orm_obj

    def before_update_object(self, orm_obj, *args, **kwargs):
        return orm_obj

    def after_delete_object(self, orm_obj, *args, **kwargs):
        return orm_obj

    def before_get_object(self, orm_obj, *args, **kwargs):
        pass

    def before_get_put(self, object, *args, **kwargs):
        pass

    def before_get_patch(self, object, *args, **kwargs):
        pass
