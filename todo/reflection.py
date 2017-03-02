def class_to_str(Clz):
    return '{}.{}'.format(
        Clz.__module__,
        Clz.__name__,
    )


def str_to_class(full_name):
    parts = full_name.split('.')
    module_full_name = '.'.join(parts[:-1])
    m = __import__(module_full_name)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m
