'''
    python matchbox data store
'''

import uuid
from pymongo.connection import Connection

class Client(object):
    '''
        Client for interfacing with the matchbox data store.
    '''

    def __init__(self, dbname, collection, host='localhost', mongo_port=27017):
        self._dbname = dbname
        self._collection_name = collection
        self._host = host
        self._mongo_port = mongo_port
        self._connection = Connection(self._host, self._mongo_port)
        self._collection = self._connection[self._dbname][self._collection_name]

    @staticmethod
    def _add_suid(doc):
        if 'suid' not in doc:
            data['suid'] = str(uuid.UUID(data['_id']).int >> 64)

    def get(self, uid, **kwargs):
        if uid:
            kwargs['_id'] = uid
        return self._collection.find_one(kwargs)

    def search(self, **kwargs):
        return self._collection.find(kwargs)

    def save(self, doc):
        if '_id' not in doc:
            raise ValueError('document does not have an id, try insert first')
        self._add_suid(doc)
        return self._collection.save(doc)

    def update(self, uid, **kwargs):
        doc = self.get(uid)
        doc.update(kwargs)
        return self.save(doc)

    def insert(self, data):
        if 'name' not in data:
            raise TypeError('missing required parameter "name"')
        if '_id' not in data:
            data['_id'] = uuid.uuid4().hex
        self._add_suid(data)
        return self._collection.insert(data)

    # fuzzy name search & merging are the real work TBD
