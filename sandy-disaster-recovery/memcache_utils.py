
import functools
import pickle
import zlib

from google.appengine.api import memcache


def memcache_set_large(key, value, chunksize=950000):
    """
    Memcache a large object using pickle, zlib compression and splitting to
    chunks.

    The default chunksize is set at 95% of the GAE memcache service 1MB limit.
    """
    serialized = pickle.dumps(value, 2)
    compressed = zlib.compress(serialized)
    values = {}
    for i in xrange(0, len(compressed), chunksize):
        values['%s.%s' % (key, i//chunksize)] = compressed[i : i+chunksize]
    memcache.set_multi(values)


def memcache_get_large(key):
    " Inverse of memcache_set_large() "
    result = memcache.get_multi(['%s.%s' % (key, i) for i in xrange(32)])
    compressed = ''.join([v for k,v in sorted(result.items()) if v is not None])
    try:
        serialized = zlib.decompress(compressed)
    except zlib.error:
        return None
    try:
        original = pickle.loads(serialized)
    except:
        return None
    return original

 
def memcached(cache_tag):
    """
    Memcache decorator with a "cache tag" that groups keys so that they can be
    invalidated together.

    For a key to be returned it and its cache tag must exist.

    This function uses memcache_get_large and memcache_set_large to support
    storing objects larger than GAE's memcache limit.
    """
    def decorator(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            cache_key = '%s%s%s' % (function.__name__, str(args), str(kwargs))

            # check existence of cache tag
            client = memcache.Client()
            while True:
                tagged_cache_keys = client.gets(cache_tag)
                if tagged_cache_keys is not None:
                    # check cache tag for cache key
                    if cache_key in tagged_cache_keys:
                        # main cache lookup
                        value = memcache_get_large(cache_key)
                        if value is not None:
                            return value
                    else:
                        # reliably append cache key to cache tag
                        while True:
                            if client.cas(
                                cache_tag,
                                tagged_cache_keys + [cache_key]
                            ):
                                break
                    break

                # init the cache tag
                if client.add(cache_tag, [cache_key]):
                    tagged_cache_keys = client.gets(cache_tag)
                    break

            # cache miss (in tag or direct) => compute & cache
            value = function(*args, **kwargs)
            memcache_set_large(cache_key, value)
            return value
        return wrapper
    return decorator


def invalidate_caches(cache_tag):
    tagged_cache_keys = memcache.get(cache_tag)
    if not tagged_cache_keys:
        return
    for cache_key in tagged_cache_keys:
        memcache.delete(cache_key)
    memcache.delete(cache_tag)
