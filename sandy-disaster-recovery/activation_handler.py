
import os
import time
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
show_password_template = jinja_environment.get_template('show_password.html')



class MultipleChoiceQuestionForm(Form):

    answers = RadioField()

    def __init__(self, *args, **kwargs):
        self.question = args[1]
        super(MultipleChoiceQuestionForm, self).__init__(*args, **kwargs)

        possible_answers = [self.question.correct_answer] + \
            self.question.wrong_answers

        # randomise answers using today's date
        random.seed(time.strftime("%Y%M%d"))
        random.shuffle(possible_answers) 
        self.answers.choices = [(a, a) for a in possible_answers]
        random.seed()  # restore RNG

    def validate_answers(self, field):
        " Correct answer => valid "
        if field.data != self.question.correct_answer:
            raise validators.ValidationError()


class ActivationHandler(base.RequestHandler):

    MAX_NUM_QUESTIONS_TO_ASK = 3

    def _get_forms(self, n, seed):
        " Return random questions as prefixed forms. "
        # construct a form for all available questions
        all_questions = list(MultipleChoiceQuestion.all())
        all_forms = [
            MultipleChoiceQuestionForm(
                self.request.POST,
                question,
                prefix=unicode(question.key().id())
            )
            for question in all_questions
        ]

        # mark all question forms
        for form in all_forms:
            form.ask = False
            if form.answers.data and form.answers.data != u'None':
                form.answered = True
                if form.validate():
                    form.correct = True
                else:
                    form.correct = False
            else:
                form.answered = False
                form.correct = False

        # pick unanswered questions forms to ask next
        unanswered_forms = [form for form in all_forms if not form.answered]
        if len(unanswered_forms) > n:
            random.seed(seed)
            selected_new_question_forms = random.sample(unanswered_forms, n)
            random.seed()  # restore RNG
        else:
            selected_new_question_forms = unanswered_forms
        for form in selected_new_question_forms:
            form.ask = True

        return all_forms

    def render(self, template, **kwargs):
        " Render response, with pageblocks. "
        template_params = dict(
            self.page_blocks,
            **kwargs
        )
        self.response.out.write(template.render(template_params))

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

    def render_questions(self, seed, allow_pass=False):
        all_question_forms = self._get_forms(
            n=self.MAX_NUM_QUESTIONS_TO_ASK,
            seed=seed
        )
        self.render(
            activation_template,
            org=self.org_by_code,
            question_forms=all_question_forms,
            seed=seed,
            allow_pass=allow_pass,
        )

    def get(self):
        seed = unicode(hash(random.random()))
        self.render_questions(seed)

    def post(self):
        # check questions and ask if ok to activate 
        seed = self.request.get('seed')
        allow_pass = bool(self.request.get('allow_pass'))
        if not seed:
            self.abort(404)
        question_forms = self._get_forms(
            n=self.MAX_NUM_QUESTIONS_TO_ASK,
            seed=seed
        )
        enough_questions_answered = (
            len(filter(lambda f: f.correct, question_forms)) >= 
            self.MAX_NUM_QUESTIONS_TO_ASK
        )
        no_questions_left = (
            len(filter(lambda f: not f.answered, question_forms)) == 0
        )
        if enough_questions_answered or allow_pass:
            self.org_by_code.activate()
            self.render(
                show_password_template,
                org=self.org_by_code
            )
        elif no_questions_left:
            self.render_questions(seed, allow_pass=True)
        else:
            self.render_questions(seed)
