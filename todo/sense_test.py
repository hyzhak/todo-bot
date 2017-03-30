from todo import sense


def test_regular_task_sentence():
    assert sense.extract_sense('flowers') == [{
        'intent': 'ADD_NEW_TASK',
        'entities': [{
            'title': 'flowers',
        }],
    }]


def test_enumerate_tasks_sentence():
    assert sense.extract_sense('candies, flowers and gift card') == [{
        'intent': 'ADD_NEW_TASK',
        'entities': [{
            'title': 'candies',
        }, {
            'title': 'flowers',
        }, {
            'title': 'gift card',
        }],
    }]
