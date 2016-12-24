from . import document


async def test_create():
    task = document.TaskDocument(description='one description')
    assert task.description == 'one description'


def test_read():
    pass


def test_update():
    pass


def test_delete():
    pass
