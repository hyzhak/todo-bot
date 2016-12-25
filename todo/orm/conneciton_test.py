import asyncio
from motor import motor_asyncio
import os
import pytest

from . import base_document, connection


@pytest.fixture
@pytest.mark.asyncio
def build_db():
    def builder():
        cx = motor_asyncio.AsyncIOMotorClient(os.environ.get('TEST_MONGODB_URL', 'mongo'),
                                              io_loop=asyncio.get_event_loop())
        db = cx.get_database('test')
        return db

    return builder


@pytest.mark.asyncio
async def test_wrap_motor(build_db):
    db = build_db()
    c = connection.Connection.wrap(db)
    assert isinstance(c, connection.Connection)


@pytest.mark.asyncio
async def test_register_document(build_db):
    db = build_db()
    c = connection.Connection.wrap(db)
    c.document('test_document', base_document.BaseDocument)
    coll = c.get_collection_by_document_class(base_document.BaseDocument)
    assert coll.name == 'test_document'
    assert coll.database == db
