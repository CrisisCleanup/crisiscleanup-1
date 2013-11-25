#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
From https://github.com/nandoflorestan/bag

---

License (MIT-like)

Copyright © 2011-2013 Nando Florestan

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from functools import wraps
# Instead of wrapper.__doc__ = f.__doc__ and wrapper.__name__ = f.__name__,
# use functools.wraps.


def memoize(limit=None, keymaker=None, cache_type=dict, debug=False):
    '''memoize decorator with a lru cache.
    When full, the cache discards the least recently used value.
    You can pass cache_type=WeakValueDictionary (not tested).
    '''
    if not keymaker:
        try:
            from cPickle import dumps
        except ImportError:
            from pickle import dumps
        keymaker = lambda *a, **kw: dumps((a, kw))

    def decoratr(fn):
        cache = cache_type()
        popular = []

        @wraps(fn)
        def wrapper(*a, **kw):
            key = keymaker((a, kw))
            try:
                popular.append(popular.pop(popular.index(key)))
            except ValueError:
                cache[key] = fn(*a, **kw)
                popular.append(key)
                if limit is not None and len(popular) > limit:
                    del cache[popular.pop(0)]
            else:
                if debug:
                    print('Hit cache of {0}(). Value:\n  {1}'.format(
                        fn.__name__, key))
            return cache[key]

        wrapper.cache = cache
        wrapper.popular = popular
        wrapper.limit = limit
        wrapper.func = fn
        return wrapper
    return decoratr


if __name__ == "__main__":
    # Example usage
    # Will cache up to 100 items, dropping the least recently used if
    # the limit is exceeded.
    @memoize(100)
    def fibo(n):
        if n > 1:
            return fibo(n - 1) + fibo(n - 2)
        else:
            return n
    print(fibo(100))

    # Same as above, but with no limit on cache size
    @memoize()
    def fibonl(n):
        if n > 1:
            return fibo(n - 1) + fibo(n - 2)
        else:
            return n
    print(fibonl(100))
