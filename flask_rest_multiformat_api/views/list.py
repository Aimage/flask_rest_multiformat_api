
from flask import request
from ..serialize import serialise, apply_data_to_model
from ..utils import build_filter, loads_filters
from ..queries import get_single, get_many
from .base import BaseView
from ..log import logger


class ModelListView(BaseView):
    allowed_methods = ['GET', 'POST']

    def get_objects(self, *args, **kwargs):
        filters_dict = loads_filters(request)
        order = request.args.get('sort', '')
        order_by = request.args.get('sort_by', '')
        number_per_page = request.args.get('per_page', 50)
        number_per_page = int(number_per_page) if isinstance(number_per_page, str) and number_per_page.isdigit() else number_per_page
        page_number = request.args.get('page', 0)
        page_number = int(page_number) if isinstance(page_number, str) and page_number.isdigit() else page_number
        model_objects = get_many(self.session, self.model, filters_dict,
                                 order_by, order, number_per_page, page_number)
        return model_objects

    def get(self, *args, **kwargs):
        self.before_get(*args, **kwargs)
        orm_objs, total_page = self.get_objects(*args, **kwargs)
        logger.debug(f"get collection result:  {orm_objs} ")
        page_number = request.args.get('page', 0)
        orm_objs_json = serialise(
            orm_objs,
            self,
            page_number=page_number,
            total_page=total_page,
        )
        return orm_objs_json, 200

    def post(self, *args, **kwargs):
        code = 201
        data = self.data_formater.parse_data(request.data)
        self.before_post(data, *args, **kwargs)
        logger.info(f"Parsed POST DATA: {data}")
        model_obj = self.create_object(data, *args, **kwargs)
        self.after_create_object(model_obj, *args, **kwargs)
        response = serialise(model_obj, self)
        self.after_post(model_obj, args, kwargs)
        return response, code

    def create_object(self, data, *args, **kwargs):
        is_many = isinstance(data, list)
        model_obj = self.schema().load(data,
                                       many=is_many,
                                       session=self.session)
        if is_many:
            for model in model_obj:
                self.session.add(model)
        else:
            self.session.add(model_obj)
        self.session.commit()
        return model_obj

    def after_create_object(self, new_object, *args, **kwargs):
        pass

    def before_post(self, data, *args, **kwargs):
        pass

    def before_get(self, *args, **kwargs):
        pass

    def after_post(self, new_object, args, kwargs):
        pass


