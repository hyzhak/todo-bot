from botstory.middlewares import sticker
import logging

logger = logging.getLogger(__name__)


def build_message(msg):
    return {
        'object': 'page',
        'entry': [{
            'id': 'PAGE_ID',
            'time': 1473204787206,
            'messaging': [{
                'sender': {
                    'id': 'facebook_user_id',
                },
                'recipient': {
                    'id': 'PAGE_ID'
                },
                'timestamp': 1458692752478,
                'message': {
                    'mid': 'mid.1457764197618:41d102a3e1ae206a38',
                    'seq': 73,
                    **msg,
                }
            }]
        }]
    }


def build_like():
    return build_message({
        'sticker_id': sticker.SMALL_LIKE,
    })


def build_postback(payload):
    return {
        'object': 'page',
        'entry': [{
            'id': 'PAGE_ID',
            'time': 1473204787206,
            'messaging': [{
                'sender': {
                    'id': 'facebook_user_id',
                },
                'recipient': {
                    'id': 'PAGE_ID'
                },
                'timestamp': 1458692752478,
                'postback': {
                    'payload': payload
                }
            }]
        }]
    }


__all__ = [build_like, build_message, build_postback]
