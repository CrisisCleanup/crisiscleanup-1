import logging
import time
import threading

from google.appengine.api import memcache

empty_item = "empty"

cache_lock = threading.Lock()
# This local cache always contains serialized protocol buffers.
# If it contained the actual DB entries, modifying them would
# be really bad.
local_cache = {}

def SetMulti(value_map, key_prefix, time_sec):
  now = time.clock()
  memcache.set_multi(value_map, key_prefix = key_prefix, time = time_sec)
  cache_lock.acquire(True)
  for key in value_map.keys():
    local_cache[key_prefix + key] = (now + time_sec, value_map[key])
  cache_lock.release()

def GetMulti(keys, key_prefix, time_sec):
  locals = GetLocals(keys, key_prefix)
  not_found = [id for id in locals.keys() if not locals[id]]
  remote = {}
  if len(not_found):
    remote = memcache.get_multi(not_found, key_prefix = key_prefix)
    if len(remote):
      now = time.clock()
      cache_lock.acquire(True)
      for key in remote.keys():
        local_cache[key_prefix + key] = (now + time_sec, remote[key])
      cache_lock.release()
  ret = {}
  
  for k in remote.keys():
    ret[k] = remote[k]
  for k in locals.keys():
    if locals[k]:
      ret[k] = locals[k]
  return ret

def GetKey(class_type, item_id):
  return "%s:%d" % (class_type.__name__, item_id)

def SetLocal(key, value, time_sec):
  now = time.clock()
  cache_lock.acquire(True)
  local_cache[key] = (now + time_sec, value)
  cache_lock.release()

def GetLocal(cache_key):
  now = time.clock()
  cache_lock.acquire(True)
  r = local_cache.get(cache_key)
  if not r:
    return None
  (expires, ret) = r
  if expires < now:
    ret = now
    logging.critical(cache_key)
    del local_cache[cache_key]
  cache_lock.release()
  return ret

def GetLocals(cache_keys, key_prefix = ""):
  now = time.clock()
  ret = {}
  cache_lock.acquire(True)
  values = [(key, local_cache.get(key_prefix + key)) for key in cache_keys]
  for (k,v) in values:
    if v:
      if v[0] < now:
        logging.critical(key_prefix + k)
        del local_cache[key_prefix + k]
        ret[k] = None
      else:
        ret[k] = v[1]
    else:
      ret[k] = None
  cache_lock.release()
  return ret

def GetCachedByIdAllowEmpty(class_type, cache_seconds, item_id):
  cache_key = GetKey(class_type, item_id)
  ret = GetLocal(cache_key)
  if not ret:
    ret = memcache.get(cache_key)
    if not ret:
      ret = class_type.get_by_id(item_id)
      if not ret:
        ret = empty_item
      if not memcache.set(cache_key, ret, time = cache_seconds):
        logging.critical("Failed to cache!")
    SetLocal(cache_key, ret, cache_seconds)
  return ret if ret != empty_item else None

def GetCachedById(class_type, cache_seconds, item_id):
  cache_key = GetKey(class_type, item_id)
  ret = GetLocal(cache_key)
  if not ret:
    ret = memcache.get(cache_key)
    if not ret:
      ret = class_type.get_by_id(item_id)
      if ret and not memcache.set(cache_key, ret, time = cache_seconds):
        logging.critical("Failed to cache!")
    SetLocal(cache_key, ret, cache_seconds)
  return ret

def GetAllCachedBy(class_type, cache_seconds):
  cache_key = "%s:all" % (class_type.__name__)
  ret = GetLocal(cache_key)
  if not ret:
    ret = memcache.get(cache_key)
    if not ret:
      ret = [a for a in class_type.all()]
      if not memcache.set(cache_key, ret, time = cache_seconds):
        logging.critical("Failed to cache!")
    SetLocal(cache_key, ret, cache_seconds)
  return ret

def PutAndCache(item, cache_time):
  item.put()
  cache_key = GetKey(type(item), item.key().id())
  SetLocal(cache_key, item, cache_time)
  return memcache.set(cache_key,
                      item,
                      time = cache_time)

def GetAndCache(class_type, cache_seconds, item_id):
  item = class_type.get_by_id(item_id)
  if item:
    cache_key = GetKey(class_type, item.key().id())
    SetLocal(cache_key, item, cache_seconds)
    memcache.set(cache_key,
                 item,
                 time = cache_seconds)
  return item
