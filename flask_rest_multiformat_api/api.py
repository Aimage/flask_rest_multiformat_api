
class RestApi(object):
    def __init__(self, app):
        self.app = app
        self.frefix_url = self.app.config.get("API_URL_PREFIX") or ""
        self.views = []

    def register_api(self, bleuprint, view, endpoint, url):
        view_func = view.as_view(endpoint)
        links = {}
#         detail_url = "{}<{}:{}>".format(url, pk_type, pk)
        links['self'] = url
        view.links = links
#         if 'GET' in view.allowed_methods:
#             bleuprint.add_url_rule(url, defaults={pk: None},
#                          view_func=view_func, methods=['GET',])
#         if 'POST' in view.allowed_methods:
#             bleuprint.add_url_rule(url, view_func=view_func, methods=['POST',])
        methods = [method for method in view.allowed_methods if method != 'POST']
        bleuprint.add_url_rule(url, view_func=view_func,
                         methods=view.allowed_methods)
        self.views.append({"view_func": view_func, "endpoint": endpoint})

    def register_blueprint(self, blueprint):
        self.app.register_blueprint(blueprint, url_prefix=self.frefix_url)