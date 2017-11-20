import types

from flask import request
from naga import compose


class Route:
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
        return f"{self.f}"


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
        if isinstance(rule.__url__, (tuple, list)):
            for url in rule.__url__:
                app.add_url_rule(f'/{url}', endpoint=url, view_func=rule(), methods=rule.methods)
        else:
            app.add_url_rule(f'/{rule.__url__}', endpoint=rule.__url__, view_func=rule(), methods=rule.methods)
    return app
