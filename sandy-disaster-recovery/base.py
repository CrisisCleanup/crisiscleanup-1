# Basic utilities shared across the application.

# System libraries.
import webapp2

class RequestHandler(webapp2.RequestHandler):
  """Base class for all of this app's request handlers.

  Currently just like webapp2.RequestHandler, except that it sends response
  headers to disable caching.
  """

  def __init__(self, *args, **kwargs):
    webapp2.RequestHandler.__init__(self, *args, **kwargs)
    self.disable_response_caching()

  def disable_response_caching(self):
    """Sets headers to disable response caching."""
    # Per http://stackoverflow.com/questions/49547/making-sure-a-web-page-is-not-cached-across-all-browsers.
    self.response.headers['Cache-Control'] = (
        'no-cache, no-store, must-revalidate')
    self.response.headers['Pragma'] = 'no-cache'
    self.response.headers['Expires'] = '0'
