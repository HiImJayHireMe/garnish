# garnish
Functional, RESTful Flask middleware with an eye toward easy testing, 
finely tuned low level middleware control, and low devopment cost.
    
Make creating Flask endpoints as easy as snapping together legos!
    
With the core functionality clocking in at less than 50 lines of code, it doesn't 
get much more simple or lightweight than this.

### Version
Pre-alpha -- everything subject to change!  

### Requirements
Python version: 3.6  
Libraries:
  - Flask
  - naga


### Overview and Rationale
I've found that writing Flask endpoints tends to be a very repetitive and not particularly elegant job.  So much `if request.method == 'POST': ...` and `@app.route('/blah' ...)`.  Even worse, it takes 4x or more the amount of time to write tests for your Flask endpoints.   

Building on the magic of [schemagic.web](https://github.com/HiImJayHireMe/schemagic) -- which allows you to write `POST` functions as normal Python functions -- `garnish` has extended that functionality to allow you to write normal (and easily testable) Python functions and then compose them into endpoints.  

Additionally, it allows fine-grained control of endpoint execution from dispatch to post processing.  

## Example Echo Endpoint

This is a low level but complete example of a Garnish endpoint.  Normally you would 
decompose repeated Tasks (such as `Task(lambda r: r.data)` and `SyncLayer(Task(simplejson.dumps))`)
into reusable code blocks.

```Python
# echo.py
import simplejson
from garnish import Route, Endpoint, SyncLayer, Task
from garnish.lib.utils import dapply
from lib.endpoints import postheyname, putheyname, gethomepage  

class Echo(Route):
    """A simple echo endpoint"""
    __url__ = 'echo/<path:name>'
  
    post = Endpoint(
                    # POST/PUT adapter layer
                    SyncLayer(Task(lambda r: r.data),
                              Task(lambda b: b.decode()),
                              Task(simplejson.loads)),
                              
                    # POST data processing layer
                    SyncLayer(Task(dapply(postheyname))),
                    
                    # POST/PUT output processing layer
                    SyncLayer(Task(simplejson.dumps)))
  
    get = Endpoint(
    
                # GET adapter layer
                SyncLayer(Task(lambda r: r.view_args)),
                
                # GET data processing layer    
                SyncLayer(Task(lambda x: (print(x), x)[1])),
                
                # GET output formatting layer
                SyncLayer(Task(dapply(gethomepage))))

    put = Endpoint(
    
                # POST/PUT data processing layer
                SyncLayer(Task(lambda r: r.data),
                          Task(lambda b: b.decode()),
                          Task(simplejson.loads)),
                          
                # POST data processing layer
                SyncLayer(Task(dapply(putheyname))),
                
                # POST/PUT output formatting layer
                SyncLayer(Task(simplejson.dumps)))
```

To complete your application, you only need to register your app and run!

```Python
# myapp.py  
from flask import Flask
from endpoints.echo import Echo
from garnish,garnish import garnish
  
app = Flask(__name__)
  
if __name__ == '__main__':
    garnish(app).run()
```

For a complete example, see `demo.py`


### How it works - a brief tutorial
  
  Each Route consists of a `__url__` class member and one or more `REST` methods (`Endpoint` class).  Conceptually, each endpoint is composed of data transformation `Layer`s, as seen in the diagram below.

#### Echo(Route) Diagram
| Endpoint(GET)            | Endpoint(POST)                                 |  Endpoint(PUT)                               |
|----------------------------|---------------------------------|---------------------------------|
| GET Adapter Layer          | POST/PUT Adapter Layer          | POST/PUT Adapter Layer          |
| Data Processing Layer      | POST Data Processing Layer      | PUT Data Processing Layer       |
| GET Output Formatter Layer | POST/PUT Output Formatter Layer | POST/PUT Output Formatter Layer |

 Each `Layer` consists of one or more `Task`s and a function that controls how the tasks are to be executed.  A `Task` is merely a wrapper for a function.  The `Task` function in conjunction with the `Layer` function controls the data flow for that layer and allows fine-grained low-level tuning for `Endpoint` execution.
 
 The most commonly used `Layer` is `SyncLayer` which instructs that each `Task` is to be executed sequentially and the data from one task flows directly into the next task.  However, you can define your own behavior by supplying any `Layer`-function you like -- a function that reduces over a list of callables.  
 
 For instance, if a common step in your data processing pipeline included several IO bound tasks to fetch external data, a `ConcurrentFetchLayer` might look like this:

```python
# concurrent_fetch.py
from concurrent.futures import ThreadPoolExecutor
from garnish.garnish import Layer

class ConcurrentFetchLayer(Layer):
    def __call__(self, *args, **kwargs):
        def call(t):
            return t.__call__()

        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(call, self.tasks))

        return self.f(results, *args, **kwargs)
```

You could then supply some sort of reducing function for your tasks.  

Lets say you need your Fibonnaci server to crunch some numbers for you.  You need some Fibonnaci tasks.

```python
# fib.py
import requests
from myapp import config  

class FibTask(Task):
    def __init__(self, n):
        # config.fib_server_url == "192.168.33.10/fib/{n}"

        def fib_resouce(n):
            url = config.fib_server_url.format(n=n)
            r = requests.get(url)
            res = int(r.text)
            return res

        super().__init__(partial(fib_resouce, n))

```

Now assembling your FibLayer is as easy as

```python
# fib.py
from myapp.endpoints.concurrent_fetch import ConcurrentFetchLayer

def noop_prev(f):
# subtle but important detail, the `Layer` function works as both an adapter and reducer,
# meaning you need to decide what to do with the results from the previous step.
# in this case, we're summing over the results of the tasks and discarding the 
# "noop" from the previous step
    return lambda results, prev: f(results)

FibLayer = ConcurrentFetchLayer(noop_prev(sum), FibTask(10), FibTask(20), FibTask(30))

```
You're now ready to server up an endpoint to anyone who wants to know what the sum of the 10th, 20th, and 30th Fibonacci numbers are!

```
class FibRoute(Route):
    __url__ = 'fib/'

    post = Endpoint(FibLayer, SyncLayer(Task(simplejson.dumps)))
```
