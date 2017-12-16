# encoding: utf-8
# !/usr/bin/python


"""This module define base MetaClass for different singletons MetaClasses"""

from weakref import ref


class SingletonError(BaseException):
    def __init__(self, class_name):
        super().__init__("Only one copy of {class_name} can exist".format(class_name=class_name))


class SingletonMeta(type):

    """
    |
    Base Metaclass for Singletons MetaClasses.
    |
    """

    def __new__(mcs, name, bases, dct):
        cls = super().__new__(mcs, name, bases, dct)
        orig_new = mcs._original_new(cls)
        orig_init = mcs._original_init(cls)
        orig_del = mcs._original_del(cls)
        return cls, orig_new, orig_init, orig_del

    @staticmethod
    def _original_new(cls):

        """
        return original __new__ method for current singleton class
        """

        if cls.__new__ is not object.__new__:
            orig_new = cls.__new__
        else:
            # if we haven't original __new__ method, use object.__new__
            def orig_new(cls, *args, **kwargs):
                return object.__new__(cls)

        return orig_new

    @staticmethod
    def _original_init(cls):

        """
        return original __init__ method for current singleton class
        """

        return cls.__init__

    @staticmethod
    def _original_del(cls):

        """
        return original __del__ method for current singleton class
        """

        return cls.__del__ if hasattr(cls, "__del__") else None

    @staticmethod
    def _set_methods(cls, _new_, _init_, _del_):

        """
        set new __new__, __init__, and __del__ methods in our class
        """

        cls.__new__ = _new_
        cls.__init__ = _init_
        cls.__del__ = _del_

    @staticmethod
    def _create_singleton__new__(singleton_cls, orig_new, modified_new):

        """
        create singleton __new__ function for given singleton class
        """

        # do modified_new if you calling this method from given class, and do original __new__ method otherwise
        def _new_(cls, *args, **kwargs):
            if cls is singleton_cls:
                return modified_new(cls, *args, **kwargs)
            else:
                return orig_new(cls, *args, **kwargs)

        return _new_

    @staticmethod
    def _create_singleton__init__(singleton_cls, orig_init, modified_init):

        """
        create singleton __init__ function for given singleton class
        """

        def _init_(self, *args, **kwargs):
            if self.__class__ is singleton_cls:
                modified_init(self, *args, **kwargs)
            else:
                orig_init(self, *args, **kwargs)

        return _init_

    @staticmethod
    def _create_singleton__del__(singleton_cls, orig_del, modified_del):

        """
        create singleton __del__ function for given singleton class
        """

        if orig_del:

            def _del_(self):
                if self.__class__ is singleton_cls:
                    modified_del(self)
                else:
                    orig_del(self)
        else:

            def _del_(self):
                if self.__class__ is singleton_cls:
                    modified_del(self)

        return _del_


class HardSingleton(SingletonMeta):

    """
    |
    It is metaclass which make current class and all his derived classes corresponding to Hard Singleton Pattern.
    It means, that you can create only one object of this class.
    If you try create second object of this class, it will be throw exception.
    |
    """

    def __new__(mcs, name, bases, dct):
        singleton_cls, orig_new, orig_init, orig_del = super().__new__(mcs, name, bases, dct)
        singleton_cls.__has_instance = False

        # create Singleton operations
        def _new_(cls, *args, **kwargs):

            if cls.__has_instance:
                raise SingletonError(cls.__name__)
            else:
                cls.__has_instance = True
                return orig_new(cls, *args, **kwargs)

        if orig_del:

            def _del_(self):
                self.__class__.__has_instance = False
                orig_del(self)
        else:

            def _del_(self):
                self.__class__.__has_instance = False

        singleton_new = mcs._create_singleton__new__(singleton_cls, orig_new, _new_)
        singleton_del = mcs._create_singleton__del__(singleton_cls, orig_del, _del_)

        # set new __new__, __init__ and __del__ methods in our class
        mcs._set_methods(singleton_cls, singleton_new, orig_init, singleton_del)

        return singleton_cls


class SoftSingletonV1(SingletonMeta):

    """
    |
    It is metaclass which make current class and all his derived classes corresponding to Soft Singleton Pattern.
    (first version)
    It means, that we can create only one object of this class.
    If we try create second object of this class, it will not produce him.
    It return previous object and newly call constructor of this class.
    |
    """

    def __new__(mcs, name, bases, dct):
        singleton_cls, orig_new, orig_init, orig_del = super().__new__(mcs, name, bases, dct)
        singleton_cls.__object_ref = None

        # create Singleton operations
        def _new_(cls, *args, **kwargs):

            if cls.__object_ref is None:
                obj = orig_new(cls, *args, **kwargs)
                cls.__object_ref = ref(obj)

            return cls.__object_ref()

        if orig_del:

            def _del_(self):
                self.__class__.__object_ref = None
                orig_del(self)
        else:

            def _del_(self):
                self.__class__.__object_ref = None

        singleton_new = mcs._create_singleton__new__(singleton_cls, orig_new, _new_)
        singleton_del = mcs._create_singleton__del__(singleton_cls, orig_del, _del_)

        # set new __new__, __init__ and __del__ methods in our class
        mcs._set_methods(singleton_cls, singleton_new, orig_init, singleton_del)

        return singleton_cls


class SoftSingletonV2(SingletonMeta):

    """
    |
    It is metaclass which make current class and all his derived classes corresponding Soft Singleton Pattern.
    (second version)
    It means, that we can create only one object of this class.
    If we try create second object of this class, it will not produce him.
    It return previous object but don't calls the constructor again (as in the first version).
    |
    """

    def __new__(mcs, name, bases, dct):
        singleton_cls, orig_new, orig_init, orig_del = super().__new__(mcs, name, bases, dct)
        singleton_cls.__object_ref = None
        singleton_cls.__not_init = True

        # create Singleton operations
        def _new_(cls, *args, **kwargs):

            if cls.__object_ref is None:
                obj = orig_new(cls, *args, **kwargs)
                cls.__object_ref = ref(obj)

            return cls.__object_ref()

        def _init_(self, *args, **kwargs):
            if self.__class__.__not_init:
                orig_init(self, *args, **kwargs)
                self.__class__.__not_init = False

        if orig_del:

            def _del_(self):
                self.__class__.__object_ref = None
                self.__class__.__not_init = True
                orig_del(self)
        else:

            def _del_(self):
                self.__class__.__object_ref = None
                self.__class__.__not_init = True

        singleton_new = mcs._create_singleton__new__(singleton_cls, orig_new, _new_)
        singleton_init = mcs._create_singleton__init__(singleton_cls, orig_init, _init_)
        singleton_del = mcs._create_singleton__del__(singleton_cls, orig_del, _del_)

        # set new __new__, __init__ and __del__ methods in our class
        mcs._set_methods(singleton_cls, singleton_new, singleton_init, singleton_del)

        return singleton_cls
