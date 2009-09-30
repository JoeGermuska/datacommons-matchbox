'''
    Clients for interacting with the data store either locally or via HTTP.
'''

from datetime import datetime
import uuid
from pymongo.connection import Connection
from sphinxapi import *

class LocalClient(object):
    '''
        Client for interfacing with a local instance of the data store.

        ``dbname``
            database name (required)
        ``host``
            host where mongodb is running (default: localhost)
        ``mongo_port``
            port where mongodb is running (default: 27017)
        ``default_source``
            source to set on records inserted without a `_source` attribute
    '''

    def __init__(self, dbname, host='localhost', mongo_port=27017,
                 default_source=None):
        self._dbname = dbname
        self._host = host
        self._mongo_port = mongo_port
        self._default_source = default_source
        self._connection = Connection(self._host, self._mongo_port)
        self._entity_col = self._connection[self._dbname]['entity']
        self._merged_col = self._connection[self._dbname]['merged']

    @staticmethod
    def _add_ids(doc):
        if '_id' not in doc:
            doc['_id'] = uuid.uuid4().hex
        if '_suid' not in doc:
            doc['_suid'] = str(uuid.UUID(doc['_id']).int >> 64)

    def insert(self, data):
        '''
            Insert a new entity into the data store.

            The only required attribute of the document at insert time is
            ``name``.  ``_id``, ``_suid``, ``_timestamp``, and ``_source`` will
            be added if not already present.
        '''
        if 'name' not in data:
            raise TypeError('missing required parameter "name"')
        if '_timestamp' not in data:
            data['_timestamp'] = datetime.now()
        if '_source' not in data:
            data['_source'] = self._default_source
        self._add_ids(data)
        return self._entity_col.insert(data)

    def update(self, uid, **kwargs):
        '''
            Update the entity with an id ``uid``.

            Given any number of additional kwargs, the entity referred to by
            ``uid`` will have the attributes specified in ``kwargs`` added or
            replaced.
        '''
        doc = self.get(uid)
        doc.update(kwargs)
        return self.save(doc)

    def get(self, uid=None, **kwargs):
        '''
            Get the entity referred to by ``uid``. (Returns None if not found)
        '''
        if uid:
            kwargs['_id'] = uid
        return self._entity_col.find_one(kwargs)

    def search(self, **kwargs):
        '''
            Find all entities matching attributes specified in kwargs.

            Returns an iterator over all results, search() will return all
            data in the datastore.
        '''
        return self._entity_col.find(kwargs)
    
    def name_search(self, query):
        
        # load sphinx client
        sphinx = SphinxClient()
        sphinx.SetLimits(0, 50)
        sphinx.SetIndexWeights({'entities': 1000, 'entities_metaphone': 100, 'entities_soundex': 100})
        sphinx.SetFieldWeights({'entity': 1000, 'aliases': 100})
        sphinx.SetSortMode(SPH_SORT_RELEVANCE)
        
        # do search and retrieve documents
        docs = []
        res = sphinx.Query(query)
        if res:
            for m in res['matches']:
                doc = self.get(**{'_suid': str(m['id'])})
                if doc:
                    docs.append(doc)
        return docs

    def save(self, doc):
        if '_id' not in doc or '_suid' not in doc:
            raise ValueError('document does not have an id, try insert first')
        return self._entity_col.save(doc)

    def make_merge(self, name, ids, source=None, _type=None):
        '''
            Build a merge record without saving any changes to the database.

            This method builds a new entity record that represents the merge of
            all of the ids specified in ``ids``.  It is necessary to provide a
            ``name`` for the new record, ``source`` and ``_type`` can also be
            provided to override the defaults.

            See ``commit_merge`` for information on saving the created merge
            record to the database.
        '''
        # initialize a merge result
        result = {'name': name, '_merged_from': ids, '_count': 0}
        self._add_ids(result)
        if source:
            result['_source'] = source

        # calculate count and type from merge candidates
        types = []
        aliases = set()
        candidates = [self.get(id) for id in ids]
        for c in candidates:
            result['_count'] += c.get('_count', 0)

            _type = c.get('type')
            if _type and _type not in types:
                types.append(_type)

            # add name + aliases to new aliases set
            aliases.add(c['name'])
            aliases.update(c.get('aliases', []))

            # merge other attributes
            for k,v in c.iteritems():
                if k[0] != '_' and k != 'name':
                    if k in result:
                        if isinstance(result[k], list):
                            if isinstance(v, list):
                                result[k].extend(v)
                            else:
                                result[k].append(v)
                        else:
                            if isinstance(v, list):
                                result[k] = v.append(result[k])
                            else:
                                result[k] = [result[k], v]
                    else:
                        result[k] = v

        # user supplied type or type of all candidates
        if not _type:
            if len(types) == 1:
                _type = types[0]
            else:
                pass    # TODO: handle conflicting types on merge
        result['_type'] = _type

        # name should not be one of its own aliases
        aliases.discard(name)
        result['aliases'] = list(aliases)

        return result

    def commit_merge(self, merge_record):
        '''
            Save a merge record created by ``make_merge`` to the database.

            Given a record created by ``make_merge`` insert the new record and
            move all merged data into the merged record collection.
        '''
        to_remove = merge_record['_merged_from']
        spec = {'_id':{'$in':to_remove}}
        old_recs = list(self._entity_col.find(spec))
        self.insert(merge_record)
        self._entity_col.remove(spec)
        self._merged_col.insert(old_recs)
