from . import base_document


async def test_create():
    document = base_document.BaseDocument(one_field='one field')
    assert document.one_field == 'one field'


def test_read():
    pass


def test_update():
    pass


def test_delete():
    pass
