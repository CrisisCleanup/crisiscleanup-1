from google.appengine.api import memcache

empty_item = "empty"

def GetCachedByIdAllowEmpty(class_type, cache_seconds, item_id):
  cache_key = "%s:%d" % (class_type.__name__, item_id)
  ret = memcache.get(cache_key)
  if not ret:
    ret = class_type.get_by_id(item_id)
    if not ret:
      ret = empty_item
    if not memcache.set(cache_key, ret, time = cache_seconds):
      logging.critical("Failed to cache!")
  return ret if ret != empty_item else None

def GetCachedById(class_type, cache_seconds, item_id):
  cache_key = "%s:%d" % (class_type.__name__, item_id)
  ret = memcache.get(cache_key)
  if not ret:
    ret = class_type.get_by_id(item_id)
    if ret and not memcache.set(cache_key, ret, time = cache_seconds):
      logging.critical("Failed to cache!")
  return ret

def GetAllCachedBy(class_type, cache_seconds):
  cache_key = "%s:all" % (class_type.__name__)
  ret = memcache.get(cache_key)
  if not ret:
    ret = [a for a in class_type.all()]
    if not memcache.set(cache_key, ret, time = cache_seconds):
      logging.critical("Failed to cache!")
  return ret
