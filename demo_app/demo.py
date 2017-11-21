import simplejson
from flask import Flask, render_template

from garnish.garnish import Route, Endpoint, SyncLayer, Task, garnish
from garnish.lib.routes import SimpleRoute
from garnish.lib.utils import dapply

app = Flask(__name__)


def epname(start):
    return lambda name: f"{start}: hey {name}"


postheyname = epname('POST')
getheyname = epname('GET')
putheyname = epname('PUT')


def gethomepage(name):
    return render_template('index.html', name=name)


class Echo(Route):
    __url__ = '/echo/<path:name>'

    post = Endpoint(SyncLayer(Task(lambda r: r.data),
                              Task(lambda b: b.decode()),
                              Task(simplejson.loads)),
                    SyncLayer(Task(dapply(postheyname))),
                    SyncLayer(Task(simplejson.dumps)))

    get = Endpoint(SyncLayer(Task(lambda r: r.view_args or {'name': None}), Task(dapply(gethomepage))))

    put = Endpoint(SyncLayer(Task(lambda r: r.data),
                             Task(lambda b: b.decode()),
                             Task(simplejson.loads)),
                   SyncLayer(Task(dapply(postheyname))),
                   SyncLayer(Task(simplejson.dumps)))


from demo_app.lib.fib import FibRoute

FibRoute = FibRoute


class Repeat(SimpleRoute):
    __url__ = '/repeat/<token>'

    def get(self, token):
        return simplejson.dumps(token)


if __name__ == '__main__':
    garnish(Flask(__name__), Echo, Repeat, FibRoute).run(debug=True, port=5000)
