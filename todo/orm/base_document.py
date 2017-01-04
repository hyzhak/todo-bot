class BaseQuerySet:
    def __init__(self, document, collection):
        self._document = document
        self._collection_obj = collection
        self._cursor_obj = None

    def __call__(self, q_obj=None, class_check=True, read_preference=None,
                 **query):
        # query = Q(**query)
        # if q_obj:
        #     # make sure proper query object is passed
        #     if not isinstance(q_obj, QNode):
        #         msg = ('Not a query object: %s. '
        #                'Did you intend to use key=value?' % q_obj)
        #         raise InvalidQueryError(msg)
        #     query &= q_obj
        queryset = self.clone()

        # queryset._query_obj &= query
        # queryset._mongo_query = None
        # queryset._cursor_obj = None
        # queryset._class_check = class_check

        return queryset

    def clone(self):
        """Creates a copy of the current
          :class:`~mongoengine.queryset.QuerySet`

        .. versionadded:: 0.5
        """
        return self.clone_into(self.__class__(self._document, self._collection_obj))

    def clone_into(self, cls):
        """Creates a copy of the current
          :class:`~mongoengine.queryset.base.BaseQuerySet` into another child class
        """
        if not isinstance(cls, BaseQuerySet):
            raise OperationError(
                '%s is not a subclass of BaseQuerySet' % cls.__name__)

        # TODO:
        # copy_props = ('_mongo_query', '_initial_query', '_none', '_query_obj',
        #               '_where_clause', '_loaded_fields', '_ordering', '_snapshot',
        #               '_timeout', '_class_check', '_slave_okay', '_read_preference',
        #               '_iter', '_scalar', '_as_pymongo', '_as_pymongo_coerce',
        #               '_limit', '_skip', '_hint', '_auto_dereference',
        #               '_search_text', 'only_fields', '_max_time_ms')
        #
        # for prop in copy_props:
        #     val = getattr(self, prop)
        #     setattr(cls, prop, copy.copy(val))

        if self._cursor_obj:
            cls._cursor_obj = self._cursor_obj.clone()

        return cls


class QuerySet(BaseQuerySet):
    def query_items(self):
        # TODO: should use real query
        return self._collection_obj.find({'name': 'hamlet'})

    def __await__(self):
        return self.query_items().to_list(None).__await__()

    async def count(self):
        return await self.query_items().count()

    async def getitem(self, index):
        l = await self.query_items().skip(index).limit(1).to_list(None)
        return l[0]

    # async def __len__(self):
    #     """Since __len__ is called quite frequently (for example, as part of
    #     list(qs)), we populate the result cache and cache the length.
    #     """
    #     if self._len is not None:
    #         return self._len
    #
    #     # Populate the result cache with *all* of the docs in the cursor
    #     if self._has_more:
    #         list(self._iter_results())
    #
    #     # Cache the length of the complete result cache and return it
    #     self._len = len(self._result_cache)
    #     return self._len


class QuerySetManager:
    get_queryset = None
    default = QuerySet

    def __get__(self, instance, owner):
        """Descriptor for instantiating a new QuerySet object when
        Document.objects is accessed.
        """
        if instance is not None:
            # Document object being used rather than a document class
            return self

        # owner is the document that contains the QuerySetManager
        queryset_class = owner._meta.get('queryset_class', self.default)
        queryset = queryset_class(owner, owner._get_collection())
        if self.get_queryset:
            arg_count = self.get_queryset.func_code.co_argcount
            if arg_count == 1:
                queryset = self.get_queryset(queryset)
            elif arg_count == 2:
                queryset = self.get_queryset(owner, queryset)
            else:
                queryset = partial(self.get_queryset, owner, queryset)
        return queryset


class MetaDocument(type):
    def __new__(cls, name, bases, attrs, **kwds):
        flattened_bases = cls._get_bases(bases)

        # super_new = super(DocumentMetaclass, cls).__new__
        super_new = type.__new__

        # EmbeddedDocuments could have meta data for inheritance
        if 'meta' in attrs:
            attrs['_meta'] = attrs.pop('meta')

        # EmbeddedDocuments should inherit meta data
        if '_meta' not in attrs:
            meta = MetaDict()
            for base in flattened_bases[::-1]:
                # Add any mixin metadata from plain objects
                if hasattr(base, 'meta'):
                    meta.merge(base.meta)
                elif hasattr(base, '_meta'):
                    meta.merge(base._meta)
            attrs['_meta'] = meta
            attrs['_meta']['abstract'] = False  # 789: EmbeddedDocument shouldn't inherit abstract

        # If allow_inheritance is True, add a "_cls" string field to the attrs
        if attrs['_meta'].get('allow_inheritance'):
            StringField = _import_class('StringField')
            attrs['_cls'] = StringField()

        new_class = super_new(cls, name, bases, attrs)
        new_class.members = tuple(attrs)
        new_class.objects = QuerySetManager()

        return new_class

    @classmethod
    def _get_bases(cls, bases):
        if isinstance(bases, BasesTuple):
            return bases
        seen = []
        bases = cls.__get_bases(bases)
        unique_bases = (b for b in bases if not (b in seen or seen.append(b)))
        return BasesTuple(unique_bases)

    @classmethod
    def __get_bases(cls, bases):
        for base in bases:
            if base is object:
                continue
            yield base
            for child_base in cls.__get_bases(base.__bases__):
                yield child_base


class MetaDict(dict):
    """Custom dictionary for meta classes.
    Handles the merging of set indexes
    """
    _merge_options = ('indexes',)

    def merge(self, new_options):
        for k, v in new_options.items():
            # for k, v in new_options.iteritems():
            if k in self._merge_options:
                self[k] = self.get(k, []) + v
            else:
                self[k] = v


class BasesTuple(tuple):
    """Special class to handle introspection of bases tuple in __new__"""
    pass


class BaseDocument(metaclass=MetaDocument):
    def __init__(self, **values):
        for key, value in values.items():
            setattr(self, key, value)

    @classmethod
    def _get_collection(cls):
        return cls.connection.get_collection_by_document_class(cls)

    async def save(self):
        pass
