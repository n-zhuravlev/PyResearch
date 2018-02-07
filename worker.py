from weakref import ref
from threading import Thread
from time import sleep


class SimpleWorker(Thread):

    """
    |
    This class creates simple worker's object.
    Worker's object is a wrapper above threads.
    This object can create new thread, in which it doing our custom function and falls asleep to some time.
    For example you can write logs in new worker.
    |
    """

    @staticmethod
    def __get_func_weakref(func):

        # create weak reference to given function
        if hasattr(func, "__self__"):
            # func is a class method
            obj = ref(func.__self__)
            method = ref(func.__func__)

            def func_weakref():
                if obj() is not None:
                    method()(obj())
                    return True
                else:
                    return False
        else:
            # func is a global function
            method = ref(func)

            def func_weakref():
                if method() is not None:
                    method()()
                    return True
                else:
                    return False

        return func_weakref

    def __init__(self, func, interval, daemon=False):

        """
        |
        :param func: our custom function, which will be called or class with __call__ method.
        :param interval: int, sleeping interval in new thread.
        :param daemon: bool, if set True, current thread will be a daemon's thread. Default False.
        |
        """

        super().__init__(daemon=daemon)
        self.__interval = interval
        self.__func = self.__get_func_weakref(func)
        self.__stopped = False

    def kill(self):

        """
        |
        Kill this worker.
        This method stopping current worker.
        |
        """

        self.__stopped = True
        self.join()

    def run(self):

        while True:
            sleep(self.__interval)
            # func return True if completed successfully and False otherwise
            if self.__stopped or not self.__func():
                self.__stopped = True
                break



if __name__ == '__main__':

    class A(object):

        def foo(self):
            print(self)
            print("ARRRRR!!")

        def __del__(self):
            print("DELETE")

        def __call__(self):
            print("CALL   !!!!!!")

    a = A()
    worker = SimpleWorker(a, 2, False)
    worker.start()
    worker.kill()
    sleep(2.5)
    worker.start()
    worker.kill()
