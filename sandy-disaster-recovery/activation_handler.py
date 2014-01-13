
import os
import datetime

import jinja2

from wtforms import Form


import base
from organization import Organization


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(
        os.path.join(
            os.path.dirname(__file__),
            'templates'
        )
    )
)
activation_template = jinja_environment.get_template('activation.html')
already_activated_template = jinja_environment.get_template('already_activated.html')
activation_too_late_template = jinja_environment.get_template('activation_too_late.html')
show_password_template = jinja_environment.get_template('show_password.html')


class ActivationForm(Form):

    pass


class ActivationHandler(base.RequestHandler):

    def dispatch(self, *args, **kwargs):
        " All requests must include a valid 'code' GET param. "

        activation_code = self.request.get('code')
        if not activation_code:
            self.abort(404)

        # lookup org by activation code
        orgs_by_code = Organization.all() \
            .filter('activation_code', activation_code)
        if orgs_by_code.count() != 1:
            self.abort(404)
        self.org_by_code = orgs_by_code[0]

        # send response if already activated
        if self.org_by_code.is_active:
            self.response.out.write(
                already_activated_template.render(
                    org=self.org_by_code
                )
            )
            return

        # send response if too late
        if self.org_by_code.activate_by < datetime.datetime.utcnow():
            self.response.out.write(
                activation_too_late_template.render(
                    org=self.org_by_code
                )
            )
            return

        # construct form
        self.form = ActivationForm(self.request.POST)

        # continue handling request
        super(ActivationHandler, self).dispatch(*args, **kwargs)

    def get(self):
        # send activation page
        self.response.out.write(
            activation_template.render({
                'org': self.org_by_code,
                'form': self.form,
            })
        )

    def post(self):
        # check ok to activate 
        if self.form.validate():
            # activate and show password
            self.org_by_code.activate()
            self.response.out.write(
                show_password_template.render({
                    'org': self.org_by_code,
                })
            )
            return
