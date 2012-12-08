#!/usr/bin/env python
#
# Copyright 2012 Jeremy Pack
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import cPickle
import logging
import time
import thread

from google.appengine.api import memcache

class LocalCache(object):
  lock = thread.allocate_lock()
  entries = {}
  def Set(self, key, val, expire_seconds):
    current_time = time.time()
    self.lock.acquire()
    self.entries[key] = (cPickle.dumps(val), expire_seconds + current_time)
    self.lock.release()

  def Get(self, key):
    current_time = time.time()
    self.lock.acquire()
    val = self.entries.get(key)
    if not val:
      ret_val = None
    elif val[1] < current_time:
      del self.entries[key]
      ret_val = None
    else:
      ret_val = cPickle.loads(val[0])
    self.lock.release()
    return ret_val

local_cache = LocalCache()


empty_item = "empty"

def GetKey(class_type, item_id):
  return "%s:%d" % (class_type.__name__, item_id)

def GetCachedByIdAllowEmpty(class_type, cache_seconds, item_id):
  cache_key = GetKey(class_type, item_id)
  ret = memcache.get(cache_key)
  if not ret:
    ret = class_type.get_by_id(item_id)
    if not ret:
      ret = empty_item
    if not memcache.set(cache_key, ret, time = cache_seconds):
      logging.critical("Failed to cache!")
  return ret if ret != empty_item else None

def GetCachedById(class_type, cache_seconds, item_id):
  cache_key = GetKey(class_type, item_id)
  ret = local_cache.Get(cache_key)
  if ret:
    return ret
  ret = memcache.get(cache_key)
  if not ret:
    ret = class_type.get_by_id(item_id)
    if ret and not memcache.set(cache_key, ret, time = cache_seconds):
      logging.critical("Failed to cache!")
  local_cache.Set(cache_key, ret, cache_seconds)
  return ret

def GetAllCachedBy(class_type, cache_seconds):
  cache_key = "%s:all" % (class_type.__name__)
  ret = local_cache.Get(cache_key)
  if ret:
    return ret
  ret = memcache.get(cache_key)
  if not ret:
    ret = [a for a in class_type.all()]
    if not memcache.set(cache_key, ret, time = cache_seconds):
      logging.critical("Failed to cache!")
  local_cache.Set(cache_key, ret, cache_seconds)
  return ret

def PutAndCache(item, cache_time):
  item.put()
  cache_key = GetKey(type(item), item.key().id())
  local_cache.Set(cache_key, item, cache_time)
  return memcache.set(cache_key,
                      item,
                      time = cache_time)

def GetAndCache(class_type, cache_seconds, item_id):
  item = class_type.get_by_id(item_id)
  if item:
    cache_key = GetKey(class_type, item.key().id())
    local_cache.Set(cache_key, item, cache_seconds)
    memcache.set(cache_key,
                 item,
                 time = cache_seconds)
  return item
