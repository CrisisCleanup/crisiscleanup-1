import unittest
from google.appengine.ext import db
from google.appengine.ext import testbed
from google.appengine.datastore import datastore_stub_util


from models import incident_definition
from datetime import datetime
class IncidentDefinitionTestCase(unittest.TestCase):

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

  def testSaveOne(self):
    incident_version = "1"
    incident_full_name = "full incident name"
    incident_short_name = "short name"
    timezone = "timezone"
    start_date_object = datetime.strptime("11/01/2012", "%m/%d/%Y").date()
    end_date_object = datetime.strptime("11/01/2013", "%m/%d/%Y").date()
    incident_date_object = datetime.strptime("11/01/2012", "%m/%d/%Y").date()
    work_order_prefix = "A"
    centroid_latitude = "41.89"
    centroid_longitude = "-89.10"
    
    inc_def = incident_definition.IncidentDefinition(version = incident_version, full_name = incident_full_name, short_name = incident_short_name, timezone = timezone, start_date = start_date_object, end_date = end_date_object, incident_date = incident_date_object, work_order_prefix = work_order_prefix, centroid_lat = centroid_latitude, centroid_lng = centroid_longitude)    
    
    # Put one entity
    inc_def.put()
    db.put([inc_def])
    
    #make sure it saves only one
    query = incident_definition.IncidentDefinition.all()
    results = query.fetch(1)
    self.assertEqual(1, len(results))
    
    

if __name__ == '__main__':
    unittest.main()