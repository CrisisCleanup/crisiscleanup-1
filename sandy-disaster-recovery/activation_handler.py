
import os
import datetime
import random

import jinja2

from wtforms import Form, RadioField, validators


import base
from organization import Organization
from question_db import MultipleChoiceQuestion
import page_db


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


class MultipleChoiceQuestionForm(Form):

    answers = RadioField()

    def __init__(self, *args, **kwargs):
        self.question = args[1]
        super(MultipleChoiceQuestionForm, self).__init__(*args, **kwargs)

        possible_answers = [self.question.correct_answer] + \
            self.question.wrong_answers

        # randomise order of answers
        random.shuffle(possible_answers) 
        self.answers.choices = [(a, a) for a in possible_answers]

    def validate_answers(self, field):
        " Correct answer => valid "
        if field.data != self.question.correct_answer:
            raise validators.ValidationError()


class ActivationHandler(base.RequestHandler):

    MAX_NUM_QUESTIONS_TO_ASK = 3

    def dispatch(self, *args, **kwargs):
        " All requests must have valid, in-date activation codes. "

        self.page_blocks = page_db.get_page_block_dict()

        self.activation_code = self.request.get('code')
        if not self.activation_code:
            self.abort(404)

        # lookup org by activation code
        orgs_by_code = Organization.all() \
            .filter('activation_code', self.activation_code)
        if orgs_by_code.count() != 1:
            self.abort(404)
        self.org_by_code = orgs_by_code[0]

        # send response if already activated
        if self.org_by_code.is_active:
            self.render(
                already_activated_template,
                org=self.org_by_code
            )
            return

        # send response if too late
        if self.org_by_code.activate_by < datetime.datetime.utcnow():
            self.render(
                activation_too_late_template,
                org=self.org_by_code
            )
            return

        # continue handling request
        super(ActivationHandler, self).dispatch(*args, **kwargs)

    def render(self, template, **kwargs):
        " Render a template, including page blocks. "
        page_blocks = page_db.get_page_block_dict()
        template_params = dict(
            page_blocks,
            **kwargs
        )
        self.response.out.write(
            template.render(
                template_params
            )
        )

    def get(self):
        # get questions
        all_questions = list(MultipleChoiceQuestion.all())
        forms = [MultipleChoiceQuestionForm(None, q) for q in all_questions]

        # if no questions are defined, activate immediately
        if not all_questions:
            self.org_by_code.activate()

        # render page
        self.render(
            activation_template,
            org=self.org_by_code,
            question_forms=forms,
            num_questions_to_ask=self.MAX_NUM_QUESTIONS_TO_ASK,
        )

    def post(self):
        " Activate the org - used by AJAX from page. "
        self.org_by_code.activate()
