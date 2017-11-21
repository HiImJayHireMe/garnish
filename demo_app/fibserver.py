from demo_app.lib.fib import FibRoute
from flask import Flask
from garnish.garnish import garnish

FibRoute = FibRoute

if __name__ == '__main__':
    garnish(Flask(__name__), FibRoute).run(debug=True, port=5001)
