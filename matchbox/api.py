'''
    python matchbox data store
'''

from datetime import datetime
import uuid
from pymongo.connection import Connection

class Client(object):
    '''
        Client for interfacing with the matchbox data store.
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
        if 'name' not in data:
            raise TypeError('missing required parameter "name"')
        if '_timestamp' not in data:
            data['_timestamp'] = datetime.now()
        if '_source' not in data:
            data['_source'] = self._default_source
        self._add_ids(data)
        return self._entity_col.insert(data)

    def update(self, uid, **kwargs):
        doc = self.get(uid)
        doc.update(kwargs)
        return self.save(doc)

    def get(self, uid, **kwargs):
        if uid:
            kwargs['_id'] = uid
        return self._entity_col.find_one(kwargs)

    def search(self, **kwargs):
        return self._entity_col.find(kwargs)

    def save(self, doc):
        if '_id' not in doc or '_suid' not in doc:
            raise ValueError('document does not have an id, try insert first')
        return self._entity_col.save(doc)

    def make_merge(self, name, ids, source=None, _type=None):
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
        self._entity_col.insert(result)
