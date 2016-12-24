import asyncio
from motor import motor_asyncio
import os
import pytest

from . import connection


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
