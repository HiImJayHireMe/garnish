import types

from flask import request
from naga import compose


class Route:
    f"""A Route is what flask hits as an endpoint.  Each rule should have a __url__ class member and
    one or more class method composed of Endpoints with the rest method in lowercase.  See demo.Echo in demo.py"""

    methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE',
               'COPY', 'HEAD', 'OPTIONS', 'LINK', 'UNLINK',
               'PURGE', 'LOCK', 'UNLOCK', 'PROPFIND', 'VIEW']

    def dispatch(self, request):
        return getattr(self, request.method.lower())

    def __call__(self, *args, **kwargs):
        return self.dispatch(request)(request)


class Task:
    def __init__(self, f):
        self.f = f

    def __call__(self, *args, **kwargs):
        return self.f(*args, **kwargs)

    def __repr__(self):
        return f"{self.f.__name__}"


class Layer:
    def __init__(self, f: types.FunctionType, *tasks: Task):
        self.f = f
        self.tasks = tasks

    def __call__(self, *args, **kwargs):
        return self.f(self.tasks, *args, **kwargs)

    def __repr__(self):
        return f"Layer({self.tasks})"


class Endpoint:
    def __init__(self, *layers):
        self.layers = layers

    def __call__(self, *args, **kwargs):
        return compose(self.layers, request)

    def __repr__(self):
        return '\n'.join(f"{layer.__class__}: {layer}" for layer in self.layers)


class SyncLayer(Layer):
    def __init__(self, *tasks):
        super(SyncLayer, self).__init__(compose, *tasks)


def garnish(app):
    for rule in Route.__subclasses__():
        app.add_url_rule(f'/{rule.__url__}', endpoint=rule.__url__, view_func=rule(), methods=rule.methods)
    return app
