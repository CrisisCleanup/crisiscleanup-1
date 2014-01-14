
from google.appengine.ext import db


class MultipleChoiceQuestion(db.Model):

    question = db.StringProperty(required=True)
    correct_answer = db.StringProperty(required=True)
    wrong_answers = db.StringListProperty()
    explanation = db.StringProperty()
