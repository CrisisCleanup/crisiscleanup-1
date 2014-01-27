# Copyright 2013 Chris Wood 
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from time import sleep
from xml.sax.saxutils import unescape

from wtforms import Form, TextAreaField, validators, FieldList


from admin_base import AdminAuthenticatedHandler

from question_db import MultipleChoiceQuestion


class MultipleChoiceQuestionEditForm(Form):

    def __init__(self, *args, **kwargs):
        # attach question object to form for ease of retrieval
        self.question_obj = args[1] if len(args) >= 2 else None
        super(MultipleChoiceQuestionEditForm, self).__init__(*args, **kwargs)
    
    question = TextAreaField('Question', [
        validators.Length(min=1, max=1000)
    ])
    correct_answer = TextAreaField('Correct Answer', [
        validators.Length(min=1, max=1000)
    ])
    wrong_answers = FieldList(
        TextAreaField('Wrong Answer', [
            validators.optional(),
            validators.Length(max=1000)
        ]),
        min_entries=3
    )
    explanation = TextAreaField('Explanation', [
        validators.Length(min=1, max=1000)
    ])


class AdminValidationQuestionsHandler(AdminAuthenticatedHandler):

    template = "admin_validation_questions.html"

    accessible_to_local_admin = False


    def _get_forms(self):
        # unescape POST to allow HTML in forms
        for k in self.request.POST.keys():
            self.request.POST[k] = unescape(self.request.POST[k])

        # load by all questions and order by id
        questions = list(MultipleChoiceQuestion.all())
        questions.sort(key=lambda q: q.key().id())

        # create forms
        posted_prefix = self.request.POST.get('prefix', '')
        existing_question_forms = [
            MultipleChoiceQuestionEditForm(
                self.request.POST
                if posted_prefix.startswith(unicode(question.key().id()))
                else None,
                question,
                prefix=unicode(question.key().id())
            )
            for question in questions
        ]
        new_question_form = MultipleChoiceQuestionEditForm(self.request.POST)
        return existing_question_forms, new_question_form

    def AuthenticatedGet(self, org, event):
        existing_question_forms, new_question_form = self._get_forms()
        self.render(
            existing_question_forms=existing_question_forms,
            new_question_form=new_question_form,
        )

    def AuthenticatedPost(self, org, event):
        action = self.request.get('action')
        existing_question_forms, new_question_form = self._get_forms()

        if action == 'create':
            # create new question
            form = new_question_form
            if form.validate():
                question = MultipleChoiceQuestion(
                    question=form.question.data,
                    correct_answer=form.correct_answer.data,
                    wrong_answers=[
                        field.data for field
                        in form.wrong_answers.entries
                        if field.data
                    ],
                    explanation=form.explanation.data
                )
                question.save()
                sleep(2)  # hack for possible datastore consistency
                self.redirect(self.request.path)

        elif action == 'edit':
            # edit existing question
            edited_form = [
                form for form in existing_question_forms
                if form._prefix == self.request.get('prefix')
            ][0]
            if edited_form.validate():
                edited_form.populate_obj(edited_form.question_obj)
                edited_form.question_obj.save()
                sleep(2)  # hack for possible datastore consistency
                self.redirect(self.request.path)

        elif action == 'delete':
            # delete existing question
            edited_form = [
                form for form in existing_question_forms
                if form._prefix == self.request.get('prefix')
            ][0]
            edited_form.question_obj.delete()
            sleep(2)  # hack for possible datastore consistency
            self.redirect(self.request.path)

        else:
            # unknown action
            self.abort(404)

        # fallen through due to errors: render page
        self.render(
            existing_question_forms=existing_question_forms,
            new_question_form=new_question_form,
        )
