
import os

import webapp2


class AbstractCronHandler(webapp2.RequestHandler):

    def dispatch(self, *args, **kwargs):
        " Allow only requests from cron or on the development server. "
        allowed = (
            self.request.headers.get('X-Appengine-Cron') == 'true' or
            os.environ['SERVER_SOFTWARE'].startswith('Development')
        )
        allowed = True # TEMP DEBUG - @@TODO remove this
        if not allowed:
            self.abort(403)
        super(AbstractCronHandler, self).dispatch(*args, **kwargs)
