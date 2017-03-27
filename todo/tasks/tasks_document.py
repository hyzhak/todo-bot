import humanize
from todo.orm import document, query


class TaskDocument(document.BaseDocument):
    def details(self):
        return 'Status: {}\n' \
               'Created: {}'.format(getattr(self, 'status', '?'),
                                    humanize.naturaltime(getattr(self, 'created_at', None)))


def task_details_renderer(task):
    return task.details()


def setup(db):
    TaskDocument.set_collection(db.get_collection('tasks'))
