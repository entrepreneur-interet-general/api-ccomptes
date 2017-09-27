# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask_mongoengine import MongoEngine

db = MongoEngine()


class Advice(db.Document):
    id = db.StringField(primary_key=True)
    administration = db.StringField()
    type = db.StringField()
    publication = db.DateTimeField()
    subject = db.StringField()
    topics = db.ListField(db.StringField())
    tags = db.ListField(db.StringField())
    content = db.StringField()
    short_content = db.StringField()

    def __unicode__(self):
        return self.subject
