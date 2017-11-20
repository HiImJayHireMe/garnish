from flask import Flask

from demo_app.lib.fib import FibRoute
from garnish.garnish_py.garnish import garnish

FibRoute = FibRoute

if __name__ == '__main__':
    garnish(Flask(__name__)).run(debug=True, port=5001)
