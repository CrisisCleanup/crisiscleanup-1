import unittest
from google.appengine.ext import db
from google.appengine.ext import testbed
from google.appengine.datastore import datastore_stub_util

class DemoTestCase(unittest.TestCase):

  def setUp(self):
    # First, create an instance of the Testbed class.
    self.testbed = testbed.Testbed()
    # Then activate the testbed, which prepares the service stubs for use.
    self.testbed.activate()
    # Create a consistency policy that will simulate the High Replication consistency model.
    self.policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=0)
    # Initialize the datastore stub with this policy.
    self.testbed.init_datastore_v3_stub(consistency_policy=self.policy)

  def tearDown(self):
    self.testbed.deactivate()

  def testEventuallyConsistentGlobalQueryResult(self):
    class TestModel(db.Model):
      pass

    user_key = db.Key.from_path('User', 'ryan')
    # Put two entities
    db.put([TestModel(parent=user_key), TestModel(parent=user_key)])

    # Global query doesn't see the data.
    self.assertEqual(0, TestModel.all().count(3))
    # Ancestor query does see the data.
    self.assertEqual(2, TestModel.all().ancestor(user_key).count(3))

if __name__ == '__main__':
    unittest.main()