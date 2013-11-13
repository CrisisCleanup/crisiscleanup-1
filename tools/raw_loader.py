
"""
Script that can be run on appengine's Interactive Console
to examine entities using the low level API

Based on http://stackoverflow.com/questions/19842671/migrating-data-when-changing-an-ndb-fields-property-type/19848970#19848970
"""

from google.appengine.api import datastore
from google.appengine.api import datastore_errors

def get_entities(keys):
    rpc = datastore.GetRpcFromKwargs({})
    keys, multiple = datastore.NormalizeAndTypeCheckKeys(keys)
    entities = None
    try:
        entities = datastore.Get(keys, rpc=rpc)
    except datastore_errors.EntityNotFoundError:
        assert not multiple

    return entities

def put_entities(entities):
    rpc = datastore.GetRpcFromKwargs({})
    keys = datastore.Put(entities, rpc=rpc)
    return keys


import my_entities
 
START_OFFSET = 0
MAX_OFFSET = 2000
CHUNK_SIZE = 100
FIELD_NAME = 'X'
 
i = 0

while True:
    offset = START_OFFSET + i * CHUNK_SIZE
    if offset > MAX_OFFSET: break
    keys = my_entities.MyEntity.all(keys_only=True).fetch(limit=CHUNK_SIZE, offset=offset)
    if not keys: break
    results = get_entities(keys)
    print set([type(result[FIELD_NAME]) for result in results])
    i += 1
