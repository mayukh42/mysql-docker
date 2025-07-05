from peewee import *
from datetime import datetime
import uuid
from utils import UNIXTIME

DB_PROXY_SRC = Proxy()
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

class BaseModel(Model):
    class Meta:
        database = DB_PROXY_SRC

class CrawlData(BaseModel):
    id = AutoField()
    crawlID = CharField(default=uuid.uuid4)
    target = CharField()
    url = CharField()
    success = BooleanField(default=True)
    status = IntegerField()
    encoding = CharField()
    headers = TextField()
    headersCount = IntegerField()
    responseLength = IntegerField()
    crawledAt = DateTimeField(default=datetime.now, formats=[DATETIME_FORMAT])
    
    def prepare_row(self, **kwargs):
        status = kwargs["status"]
        headers = kwargs.get("headers", {})
        return {
            "crawlID": uuid.uuid4(),
            "target": kwargs["target"],
            "url": kwargs["url"],
            "status": status,
            "success": status == 200 or status == 201,
            "encoding": kwargs["encoding"],
            "headers": headers,
            "headersCount": len(headers.keys()),
            "responseLength": kwargs["responseLength"]
        }


def create_table(model, table_name):
    try:
        model._meta.set_table_name(table_name)
        model.create_table()
    except Exception as e:
        raise e


def custom_table_name(model):
    return "{}_{}".format(model.__name__, UNIXTIME)
