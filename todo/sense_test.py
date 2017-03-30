from todo import sense


def test_regular_task_sentence():
    assert sense.extract_sense('flowers') == [{
        'intent': 'ADD_NEW_TASK',
        'entities': [{
            'title': 'flowers',
        }],
    }]
