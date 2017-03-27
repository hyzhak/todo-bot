from todo import reflection


class TestClz:
    pass


def test_class_to_str():
    assert reflection.class_to_str(TestClz) == 'todo.reflection_test.TestClz'


def test_str_to_class():
    assert reflection.str_to_class('todo.reflection_test.TestClz') == TestClz


def test_none_str_to_none_class():
    assert reflection.str_to_class(None) is None


def my_sqr(value):
    return value * value


def test_could_reflect_func():
    _my_sqr = reflection.str_to_class(reflection.class_to_str(my_sqr))
    assert _my_sqr(10) == 100
