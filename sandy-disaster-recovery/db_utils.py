
class BatchingQuery(object):
    """
    Wrapper for db queries to self-batch using cursors.

    Includes garbage collection help, as suggested at
    http://stackoverflow.com/questions/9124398
    """

    def __init__(self, query, batch_size, gc=True):
        self.query = query
        self.batch_size = batch_size
        self.gc = gc

    def __iter__(self):
        cursor = None
        while True:
            for item in self.query.fetch(self.batch_size):
                yield item
            new_cursor = self.query.cursor()
            if new_cursor == cursor:
                raise StopIteration
            else:
                cursor = new_cursor
                if self.gc:
                    import gc
                    gc.collect()
                self.query.with_cursor(cursor)
