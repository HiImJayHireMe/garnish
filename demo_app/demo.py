import simplejson
from flask import Flask, render_template

from garnish.garnish import Route, Endpoint, SyncLayer, Task, garnish
from garnish.lib.utils import dapply


def epname(start):
    return lambda name: f"{start}: hey {name}"


postheyname = epname('POST')
getheyname = epname('GET')
putheyname = epname('PUT')


def gethomepage(name):
    return render_template('index.html', name=name)


class Echo(Route):
    __url__ = 'echo/<path:name>'

    post = Endpoint(SyncLayer(Task(lambda r: r.data),
                              Task(lambda b: b.decode()),
                              Task(simplejson.loads)),
                    SyncLayer(Task(dapply(postheyname))),
                    SyncLayer(Task(simplejson.dumps)))

    get = Endpoint(SyncLayer(Task(lambda r: r.view_args)),
                   SyncLayer(Task(lambda x: (print(x), x)[1])),
                   SyncLayer(Task(dapply(gethomepage))))

    put = Endpoint(SyncLayer(Task(lambda r: r.data),
                             Task(lambda b: b.decode()),
                             Task(simplejson.loads)),
                   SyncLayer(Task(dapply(postheyname))),
                   SyncLayer(Task(simplejson.dumps)))


if __name__ == '__main__':
    garnish(Flask(__name__)).run(debug=True)
