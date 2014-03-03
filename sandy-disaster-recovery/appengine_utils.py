
import base64

from google.appengine.ext import db
from google.appengine.datastore import entity_pb


#
# serialization
#

def serialize_entity(entity):
    " Serialize an entity to a unicode-compatible form. "
    return base64.b64encode(db.model_to_protobuf(entity).Encode())


def deserialize_entity(str_or_unicode):
    " Deserialize the results of serialize_entity() "
    return db.model_from_protobuf(
        entity_pb.EntityProto(
            base64.b64decode(str_or_unicode)
        )
    )


#
# Models
#

class ModelHookMixin(object):
    """
    Base model mixin to add hooks for processing before and after puts/saves
    and deletes.

    To use the hooks, override before_put() and after_put() in child classes
    *and* ensure to call the super-method:

    e.g.
        def before_put(self):
            super(MyClass, self).before_put()
    """

    def before_put(self):
        pass
  
    def after_put(self):
        pass
  
    def put(self, **kwargs):
        self.before_put()
        result = super(ModelHookMixin, self).put(**kwargs)
        self.after_put()
        return result

    def save(self, **kwargs):
        " db.Model.save() is deprecated, but sometimes used, hence this. "
        self.before_put()
        result = super(ModelHookMixin, self).save(**kwargs)
        self.after_put()
        return result

    def before_delete(self):
        pass

    def after_delete(self):
        pass

    def delete(self, **kwargs):
        self.before_delete()
        result = super(ModelHookMixin, self).delete(**kwargs)
        self.after_delete()
        return result

class HookedModel(ModelHookMixin, db.Model): pass

class HookedExpandoModel(ModelHookMixin, db.Expando): pass


#
# Datastore
#

def generate_with_cursors(query, batch_size=20):
    cursor = None
    count = 0
    while True:
        if cursor:
            query.with_cursor(cursor)
        batch = query.fetch(batch_size)
        if not batch:
            break
        count += len(batch)
        for entity in batch:
            yield entity
        cursor = query.cursor()


#
# Search API
#

from google.appengine.api import search

def search_doc_to_dict(doc):
    return {
        field.name: field.value for field in doc.fields
    }


def search_query_str_from_params(triples):
    """
    Construct a query string for the GAE Search API
    from a list of triples of the form
        (name_of_field, coercion_funcction, value)
    """
    query_str = u''
    for field_name, coerce_fn, value in triples:
        if value is not None:
            query_str += '%s:%s ' % (field_name, coerce_fn(value))
    return query_str


def generate_from_search_with_cursors(index, query_str):
    cursor = search.Cursor()
    while cursor != None:
        search_query = search.Query(
            query_str,
            search.QueryOptions(
                cursor=cursor
            )
        )
        results = index.search(search_query)
        cursor = results.cursor
        for hit in results:
            yield hit


def generate_from_search(index, query_str, limit, offset):
    """
    Generate hits from search on index.

    Use limit & offset directly if within GAE limits [1], otherwise manually walk
    across cursor-powered query.

    Note: this in efficient to use for paging after 2000 results. Search API
    cursors [2] should be used but this function does not support them.

    [1] https://developers.google.com/appengine/docs/python/search/options#Python_QueryOptions
    [2] https://developers.google.com/appengine/docs/python/search/results#Python_Using_cursors  
    """
    if limit <= 1000 and offset <= 1000:
        # use limits and offsets
        search_query = search.Query(
            query_str,
            search.QueryOptions(
                limit=limit,
                offset=offset
            )
        )
        results = index.search(search_query)
    else:
        # search using cursor and discard up to offset
        results = generate_from_search_with_cursors(index, query_str)
        for i in xrange(offset):
            results.next()

    # yield results up to limit
    num_generated = 0 
    for hit in results:
        if num_generated == limit:
            break
        else:
            yield hit
            num_generated += 1
