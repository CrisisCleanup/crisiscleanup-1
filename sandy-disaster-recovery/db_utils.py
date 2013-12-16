
class BatchingQuery(object):

    " Wrapper for db queries to self-batch using cursors. "

    def __init__(self, query, batch_size):
        self.query = query
        self.batch_size = batch_size

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
                self.query.with_cursor(cursor)

