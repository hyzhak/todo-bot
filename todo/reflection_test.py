from todo import reflection


class TestClz:
    pass


def test_class_to_str():
    assert reflection.class_to_str(TestClz) == 'todo.reflection_test.TestClz'


def test_str_to_class():
    assert reflection.str_to_class('todo.reflection_test.TestClz') == TestClz
