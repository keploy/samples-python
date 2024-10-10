from django.db import models
from mongoengine import Document, StringField, IntField

class Item(Document):
    name = StringField(required=True)
    quantity = IntField(required=True)
    description = StringField()