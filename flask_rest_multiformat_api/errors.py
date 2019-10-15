

class ApiError(object):
    title = 'Unknown error'
    status = '500'
    source = None

    def __init__(self, detail, source="", title="", status="500",
                 code=None, id_=None, links={}, meta={}):
        self.detail = detail
        self.source = source
        self.code = code
        self.id = id_
        self.links = links or {}
        self.meta = meta or {}
        self.title = title
        self.status = status
        

class ObjectNotFoundError(ApiError):
    
    def __init__(self, model, id_object):
        title = "{} not found".format(model.__name__)
        detail = "{} {} is not available".format(model.__name__, id_object)
        super().__init__(detail, title=title, status="404", code=404)
        
    