import unittest
import datetime
from api import LocalClient

TEST_DB = 'testdb'

class TestClient(unittest.TestCase):

    def _test_doc(self, which=0):
        return {'name': 'Spacely Space Sprockets'}

    def _clear_db(self):
        self.client._connection.drop_database(TEST_DB)

    def setUp(self):
        self.default_source = 'test'
        self.client = LocalClient(TEST_DB, default_source=self.default_source)
        self._clear_db()

    def test_add_ids(self):
        doc = {}
        LocalClient._add_ids(doc)
        self.assert_('_id' in doc)
        self.assert_('_suid' in doc)
        newdoc = dict(doc)
        LocalClient._add_ids(doc)
        self.assertEqual(doc, newdoc)

    def test_insert_noname(self):
        f = lambda: self.client.insert({'spam':'eggs'})
        self.assertRaises(TypeError, f)

    def test_insert_success(self):
        self._clear_db()
        doc = self._test_doc()
        key = self.client.insert(self._test_doc())
        inserted = self.client._entity_col.find_one()
        self.assertEqual(doc['name'], inserted['name'])
        self.assertEqual(key, inserted['_id'])
        self.assertEqual(self.default_source, inserted['_source'])
        self.assert_('_suid' in inserted)
        self.assert_(isinstance(inserted['_timestamp'], datetime.datetime))

    def test_update_success(self):
        self._clear_db()
        doc = self._test_doc()
        key = self.client.insert(doc)
        self.client.update(key, makes='sprockets')
        item = self.client.get(key)
        self.assertEqual(item['makes'], 'sprockets')

    def test_make_merge_simple(self):
        self._clear_db()
        docs = [{'name': 'Spacely Space Sprockets', 'some_id': 'ABCD1', '_count':3},
                {'name': 'Spacely Sprockets', 'makes':'sprockets', '_count':4},
                {'name': "Spacely's Sprockets", 'some_id':'X100'}]
        ids = []
        for doc in docs:
            ids.append(self.client.insert(doc))
        result = self.client.make_merge(docs[0]['name'], ids)

        self.assertEqual(result['name'], 'Spacely Space Sprockets')
        self.assertEqual(result['aliases'], [u"Spacely's Sprockets", u'Spacely Sprockets'])
        self.assertEqual(result['_count'], 7)
        self.assertEqual(result['_merged_from'], ids)
        self.assertEqual(result['some_id'], [u'ABCD1', u'X100'])
        self.assertEqual(len(result['_id']), 32)

    def test_commit_merge_simple(self):
        self._clear_db()
        docs = [{'name': 'Spacely Space Sprockets', 'some_id': 'ABCD1', '_count':3},
                {'name': 'Spacely Sprockets', 'makes':'sprockets', '_count':4},
                {'name': "Spacely's Sprockets", 'some_id':'X100'}]
        ids = []
        for doc in docs:
            ids.append(self.client.insert(doc))
        merge = self.client.make_merge(docs[0]['name'], ids)
        self.client.commit_merge(merge)

        # get resulting contents of both stores
        entities = list(self.client._entity_col.find())
        merged = list(self.client._merged_col.find())
        self.assertEqual(len(entities), 1)
        self.assertEqual(entities[0]['_id'], merge['_id'])
        self.assertEqual(len(merged), 3)

# TODO: search, save, get

if __name__ == '__main__':
    unittest.main()
