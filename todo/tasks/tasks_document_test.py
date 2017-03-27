import datetime
import humanize
from unittest import mock
from . import tasks_document


def test_setup_should_pass_collection_to_document():
    fake_collection = 'some-fake-collection'
    fake_db = mock.Mock()
    fake_db.get_collection = mock.MagicMock(return_value=fake_collection)
    tasks_document.setup(fake_db)

    assert tasks_document.TaskDocument.collection == fake_collection


def test_task_details():
    created_at = datetime.datetime(year=2017, month=3, day=27, hour=23, minute=46)
    task = tasks_document.TaskDocument(**{
        'created_at': created_at,
        'status': 'open',
    })

    assert task.details() == 'Status: open\n' \
                             'Created: {}'.format(humanize.naturaltime(created_at))
