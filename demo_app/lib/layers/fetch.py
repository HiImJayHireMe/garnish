from concurrent.futures import ThreadPoolExecutor

from garnish.garnish_py.garnish import Layer


class ConcurrentFetchLayer(Layer):
    def __call__(self, *args, **kwargs):
        def call(t):
            return t.__call__()

        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(call, self.tasks))

        return self.f(results, *args, **kwargs)
