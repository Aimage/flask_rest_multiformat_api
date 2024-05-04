from flask.views import MethodView
from marshmallow import ValidationError

from flask import (abort, request, make_response)
from werkzeug.exceptions import BadRequest, MethodNotAllowed
from ..exceptions import ApiException
from ..errors import (ApiError, ObjectNotFoundError,
                                               InvalidDataError)

from ..format import DATA_FORMATER

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

        Dataformater = DATA_FORMATER.get(self.data_format, DEFAULT_FORMATER)
        self.data_formater = Dataformater()

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
                                   request.method.lower())
        assert meth is not None, 'Unimplemented method %r' % request.method
        try:
            meth = self.apply_decorators(meth)
            return meth(*args, **kwargs)
        except (ApiException, ValidationError) as e:
            if isinstance(e, ValidationError):
                errors = [InvalidDataError(e.messages)]
                return self.data_formater.build_error_response(errors)
            return self.data_formater.build_error_response(e.errors)
