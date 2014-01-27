
from google.appengine.ext import db


class MultipleChoiceQuestion(db.Model):

    question = db.TextProperty(required=True)
    correct_answer = db.TextProperty(required=True)
    wrong_answers = db.StringListProperty()
    explanation = db.TextProperty()
