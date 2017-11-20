from functools import partial

import requests
import simplejson
from naga import compose

from demo_app.lib.layers.fetch import ConcurrentFetchLayer
from garnish.garnish import Task, Route, Endpoint, SyncLayer
from garnish.lib.utils import dapply, constantly


class config:
    fib_server_url = "http://0.0.0.0:5001/fib/{n}"


class FibTask(Task):
    def __init__(self, n):
        # config.fib_server_url == "192.168.33.10/fib/{n}"

        def fib_resouce(n):
            url = config.fib_server_url.format(n=n)
            r = requests.get(url)
            res = int(r.text)
            return res

        # resource = lambda n: int(requests.get(config.fib_server_url.format(n=n)))
        super().__init__(partial(fib_resouce, n))


def noop_prev(f):
    return lambda results, prev: f(results)


FibLayer = ConcurrentFetchLayer(lambda r, prev: sum(r),
                                FibTask(10), FibTask(20), FibTask(30))

FibList = ConcurrentFetchLayer(list,
                               FibTask(10), FibTask(20), FibTask(30))


def fib(n):
    i = a = b = 1
    while True:
        if i == n:
            return b
        a, b = b, a + b
        i += 1


class FibRoute(Route):
    __url__ = ['fib/<path:n>', 'fib/']

    post = Endpoint(FibLayer, SyncLayer(Task(simplejson.dumps)))

    get = Endpoint(SyncLayer(Task(lambda r: r.view_args),
                             Task(dapply(lambda n: int(n)))),
                   SyncLayer(Task(fib)),
                   SyncLayer(simplejson.dumps))

# class FibList(Route):
#     __url__ = 'fib/list'
#
#     post = Endpoint(SyncLayer(Task(constantly(None))),
#                     FibLayer,
#                     )
