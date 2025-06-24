class fragile(object):
    class Break(Exception):
        """break out of with"""
    
    def __init__(self, value):
        self.value = value
    
    def __enter__(self):
        return self.value.__enter__()
    
    def __exit__(self, etype, value, traceback):
        error = self.value.__exit__(etype, value, traceback)
        if etype == self.Break:
            return True
        return error