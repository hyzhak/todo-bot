from unittest import mock
from . import list_document


def test_setup_should_pass_collection_to_document():
    fake_collection = 'some-fake-collection'
    fake_db = mock.Mock()
    fake_db.get_collection = mock.MagicMock(return_value=fake_collection)
    list_document.setup(fake_db)

    assert list_document.ListDocument.collection == fake_collection
