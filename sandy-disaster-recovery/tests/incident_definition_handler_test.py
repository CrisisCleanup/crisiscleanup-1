#import unittest
#import webtest
#import webapp2
#from google.appengine.ext import db
#from google.appengine.ext import testbed
#from google.appengine.datastore import datastore_stub_util

#class AppTest(unittest.TestCase):
    #def setUp(self):
        ## Create a WSGI application.
        #app = webapp2.WSGIApplication([('/', HelloWorldHandler)])
        #self.testapp = webtest.TestApp(app)

    ## Test the handler.
    #def testHelloWorldHandler(self):
        #response = self.testapp.get('/')
        #self.assertEqual(response.status_int, 200)
        #self.assertEqual(response.normal_body, 'Hello World!')
        #self.assertEqual(response.content_type, 'text/plain')

#if __name__ == '__main__':
    #unittest.main()