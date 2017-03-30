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


def test_multi_lines_tasks_sentence():
    assert sense.extract_sense('candies\nflowers\ngift card') == [{
        'intent': 'ADD_NEW_TASK',
        'entities': [{
            'title': 'candies',
        }, {
            'title': 'flowers',
        }, {
            'title': 'gift card',
        }],
    }]


def test_sentence_with_punctuation():
    assert sense.extract_sense('gift!') == [{
        'intent': 'ADD_NEW_TASK',
        'entities': [{
            'title': 'gift!',
        }],
    }]
