import logging
import re

logger = logging.getLogger(__name__)

tokenizer_reg = re.compile(r'([\W]+)')


def tokenize(text):
    return tokenizer_reg.split(text)


def strip_tokens(tokens):
    return [t.strip() if t != '\n' else t for t in tokens]


LINKED_WORDS = [',', '.', 'and', 'or', '...', '/', '\n']


def split_by_linked_words(tokens):
    sentence = []
    for t in tokens:
        if t in LINKED_WORDS:
            yield sentence
            sentence = []
        else:
            sentence.append(t)
    yield sentence


PUNCTUATION_WORDS = ['!', '?', '_', '(', ')', '#', '@', '%', '^', '\'', '"', '`']


def join_punctuation(tokens):
    for sentence in tokens:
        word = ''
        new_sentence = []
        for w in sentence:
            if w in PUNCTUATION_WORDS or len(word) == 0:
                word += w
            else:
                new_sentence.append(word)
                word = w
        new_sentence.append(word)
        yield new_sentence


def flatten_sentences(tokens):
    return [' '.join(t) for t in tokens]


def strip_empty_words(tokens):
    return [t for t in tokens if t != '']


def extract_sense(text):
    tokens = tokenize(text.strip())
    tokens = strip_tokens(tokens)
    tokens = strip_empty_words(tokens)
    tokens = split_by_linked_words(tokens)
    tokens = join_punctuation(tokens)
    tokens = flatten_sentences(tokens)
    tokens = strip_empty_words(tokens)
    return [{
        'intent': 'ADD_NEW_TASK',
        'entities': [{
                         'title': w,
                     } for w in tokens],
    }]
