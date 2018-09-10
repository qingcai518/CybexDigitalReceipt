from peewee import *
from common.Config import *


class UnknownField(object):
    def __init__(self, *_, **__): pass


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    name = CharField(primary_key=True)
    password = CharField()
    owner_pub_key = CharField()
    active_pub_key = CharField()
    memo_pub_key = CharField()
    created_at = CharField()
    update_at = CharField()

    class Meta:
        table_name = 'user'
