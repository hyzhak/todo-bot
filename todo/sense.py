def extract_sense(text):
    return [{
        'intent': 'ADD_NEW_TASK',
        'entities': [{
            'title': text,
        }],
    }]
