class Adapter:
    def __init__(self, f, *tasks):
        self.f = f
        self.tasks = tasks

    def __call__(self, *args, **kwargs):
        return self.f(self.tasks, *args, **kwargs)


NoOp = Adapter(lambda tasks, *previous: tasks)
