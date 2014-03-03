
import logging

from google.appengine.api import search
from google.appengine.api import memcache

from appengine_utils import HookedExpandoModel, serialize_entity #, deserialize_entity
from memcache_utils import invalidate_caches


class SearchIndexedExpandoModel(HookedExpandoModel):
    """
    Expando model that indexes itself using the GAE Search API on save.

    Subclasses should define indexes_and_fields() to specify what indexes to
    index to and how to represent the entity as a search document.

    Invalidation of cache tags is built-in: set CACHE_TAGS to the tag names.

    Entities are also memcached by numeric id for get_by_id().
    """

    CACHE_TAGS = set() 

    @property
    def serialized(self):
        return serialize_entity(self)

    def indexes_and_fields(self):
        " Subclasses must define what fields are to be indexed. "
        raise NotImplementedError

    def _indexes_and_docs(self):
        try:
            for search_index, fields in self.indexes_and_fields():
                search_doc = search.Document(
                    doc_id=unicode(self.key()),
                    fields=fields
                )
                yield search_index, search_doc
        except AttributeError, e:
            logging.warning(
                "Error creating index doc for %s; " % self.__class__.__name__ +
                "missing required fields - see following exception"
            )
            logging.exception(e)
  
    def index(self):
        for search_index, search_doc in self._indexes_and_docs():
            search_index.put(search_doc)

    def remove_from_indexes(self):
        for search_index, search_doc in self._indexes_and_docs():
            search_index.remove(search_doc.doc_id)
  
    @classmethod
    def index_all(cls):
        BATCH_SIZE = 20
        logging.info("Indexing all %s entities..." % cls.__name__)
        cursor = None
        count = 0
        while True:
            query = cls.all()
            if cursor:
                query.with_cursor(cursor)
            batch = query.fetch(BATCH_SIZE)
            if not batch:
                break
            count += len(batch)
            for entity in batch:
                entity.index()  # TODO could use Search API multi-puts here
            logging.info("Indexed %d..." % count)
            cursor = query.cursor()
        logging.info("Done indexing all %s entities." % cls.__name__)

    def put_to_memcache(self):
        memcache.set_multi(
            {
                unicode(self.key()): self,
                unicode(self.key().id()): self,
            },
            key_prefix=self.__class__.__name__
        )

    def delete_from_memcache(self):
        memcache.delete_multi(
            {
                unicode(self.key()): self,
                unicode(self.key().id()): self,
            },
            key_prefix=self.__class__.__name__
        )

    def _invalidate_cache_tags(self):
        for cache_tag in self.CACHE_TAGS:
            invalidate_caches(cache_tag)

    def after_put(self):
        super(SearchIndexedExpandoModel, self).after_put()
        self.index()
        self.put_to_memcache()
        self._invalidate_cache_tags()

    def after_delete(self):
        super(SearchIndexedExpandoModel, self).after_delete()
        self.remove_from_indexes()
        self.delete_from_memcache()
        self._invalidate_cache_tags()

    ##@classmethod
    ##def get(self, keys, *args, **kwargs):
    ##    # TODO: tricky because keys can be many str, Key, [str...], [Key...]

    @classmethod
    def get_by_id(cls, ids, parent=None):
        if parent is not None:
            # not supported by this cached version
            return super(SearchIndexedExpandoModel, cls).get_by_id(ids, parent=parent)

        # support single id or list of them, as per db.Model.get_by_id
        if isinstance(ids, (int, long)):
            ids = [ids]

        # try memcache
        results_d = {
            int(k): v
            for k, v
            in memcache.get_multi(
                [unicode(id) for id in ids],
                key_prefix=cls.__name__
            ).items()
        }

        # compute for any cache misses (and memcache)
        for id in ids:
            if results_d.get(id) is None:
                results_d[id] = super(SearchIndexedExpandoModel, cls).get_by_id(id)
                results_d[id].put_to_memcache()

        # return as per db.Model.get_by_id()
        if len(results_d) == 0:
            return None
        elif len(results_d) == 1:
            return results_d.values()[0]
        else:
            return [results_d[id] for id in ids]
