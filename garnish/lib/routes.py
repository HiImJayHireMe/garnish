from flask import request

from garnish import Route


class SimpleRoute(Route):
    def __call__(self, *args, **kwargs):
        return self.dispatch(request)(*args, **kwargs)
