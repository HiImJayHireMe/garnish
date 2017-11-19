# garnish
Functional, RESTful Flask middleware with an eye toward easy testing, 
finely tuned low level middleware control, and low devopment cost.
With the core functionality clocking in at only 42 lines non-whitespace code, it doesn't 
get much more simple or lightweight than this.


### Version
Pre-alpha -- everything subject to change!  

### Overview and Rationale
Writing 

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
                   SyncLayer(Task(dapply(putheyname))),
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