
import datetime
import random

from wtforms import Form, RadioField, validators

import base
from organization import Organization
from question_db import MultipleChoiceQuestion


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


class ActivationHandler(base.FrontEndAuthenticatedHandler):

    template_filenames = [
        'activation.html',
        'already_activated.html',
        'activation_too_late.html'
    ]

    MAX_NUM_QUESTIONS_TO_ASK = 3

    def pre_dispatch(self, *args, **kwargs):
        " All requests must have valid, in-date activation codes. "

        # not open to users already logged in
        if self.request.logged_in:
            self.abort(403)

        # get activation code
        activation_code = self.request.get('code')
        if not activation_code:
            self.abort(404)

        # lookup org by activation code
        orgs_by_code = Organization.all() \
            .filter('activation_code', activation_code)
        if orgs_by_code.count() != 1:
            self.abort(404)
        self.request.org_by_code = orgs_by_code[0]

        # send response if already activated
        if self.request.org_by_code.is_active:
            self.render(
                template='already_activated.html',
                org=self.request.org_by_code
            )
            raise Exception

        # send response if too late
        if self.request.org_by_code.activate_by < datetime.datetime.utcnow():
            return self.render(
                template='activation_too_late.html',
                org=self.request.org_by_code
            )
            raise Exception

    def get(self):
        # get questions
        all_questions = list(MultipleChoiceQuestion.all())
        random.shuffle(all_questions)
        forms = [MultipleChoiceQuestionForm(None, q) for q in all_questions]

        # if no questions are defined, activate immediately
        if not all_questions:
            self.request.org_by_code.activate()

        # render page
        return self.render(
            template='activation.html',
            org=self.request.org_by_code,
            question_forms=forms,
            num_questions_to_ask=self.MAX_NUM_QUESTIONS_TO_ASK,
        )

    def post(self):
        " Activate the org - used by AJAX from page. "
        self.request.org_by_code.activate()
