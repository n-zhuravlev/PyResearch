#!/usr/bin/env python3
# coding: utf8

"""This module defined time profiling class"""

from sys import stdout
from time import sleep, time


class TimeTracker(object):

    """
    |
    This class track the time and do profiling.

    Instance of this class is a context manager. It marks start time, when we input in the context and end time,
    when we output. It prints difference between end time and start time in ms/seconds/minuts/hours.

    "time" - data member stores summary time spent in every context.
    "reset" - method, which clear this time.

    You also can set/change format of time, verbosity level, output stream and time rounding.
    |
    Example:

        As a single instance.

        with TimeTracker():
            do something  possible

        >> Elapsed time 434.322118759 ms

        with TimeTracker("min"):
            do something  possible

        >> Elapsed time 0.709244732062 min

        -----------------------------------------

        As a reused instace.

        tracker = TimeTracker()

        with tracker:
            do something  possible

        >> Elapsed time 17.92348369387 ms

        -----------------------------------------

        tracker = TimeTracker(time_format="sec", verbose=2, rounding=3)

        with tracker:
            do something  possible

        tracker.format = "ms"
        tracker.rounding = 5
        print(tracker)

        >> Elapsed time:
        >> all:
        >>     2.543 sec
        >> current:
        >>     2.543 sec
        >> Elapsed time 2542.65308 ms

    |
    """

    __FORMATS = {
        "ms": 0.001,
        "sec": 1.0,
        "min": 60.0,
        "hour": 3600.0
    }

    def __init__(self, time_format="ms", verbose=0, rounding=2, stream=stdout):

        """
        |
        :param time_format: string, Type of printed time. Default print time in milliseconds.
        :param verbose: int, Verbosity level, 0, 1 or 2. Default 0.
        :param rounding: int, to round a number to a certain decimal point
        :param stream: stream for writing results. Default stdout.
        |
        "ms" - printed time expressed in milliseconds.
        "sec" - printed time expressed in seconds.
        "min" - printed time expressed in minutes.
        "hour" - printed time expressed in hours.
        |
        """

        assert time_format in TimeTracker.__FORMATS, "time_format must be a string with ms/sec/min/hour"
        assert isinstance(verbose, int) and verbose in (0, 1, 2), "verbose must be a int variable 0, 1 or 2"
        assert isinstance(rounding, int) and rounding >= 1, "rounding must be a int variable >= 1"
        assert hasattr(stream, "write") and hasattr(stream.write, "__call__"), "stream must have write method"

        self.__format = time_format
        self.__verbose = verbose
        self.__round = rounding
        self.__stream = stream
        self.__time = 0

    def __enter__(self):
        self.__start = time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__end = time()
        diff = (self.__end - self.__start) / TimeTracker.__FORMATS[self.__format]
        self.__time += diff

        if self.__verbose == 1:
            self.__stream.write("Elapsed time {time} {format}\n".format(time=round(self.__time, self.__round),
                                                                        format=self.__format))
        elif self.__verbose == 2:
            self.__stream.write("Elapsed time: \n"
                                "all:\n"
                                "\t{time1} {format}\n"
                                "current:\n"
                                "\t{time2} {format}\n".format(time1=round(self.__time, self.__round),
                                                              time2=round(diff, self.__round),
                                                              format=self.__format))

    def __str__(self):
        return "Elapsed time {time} {format}\n".format(time=round(self.__time, self.__round), format=self.__format)

    def reset(self):

        """
        |
        Reset previous time.
        |
        """

        self.__time = 0

    time = property()
    format = property()
    verbose = property()
    rounding = property()
    stream = property()

    @time.getter
    def time(self):
        return self.__time

    @format.getter
    def format(self):
        return self.__format

    @format.setter
    def format(self, new_format):
        assert new_format in TimeTracker.__FORMATS, "new time format must be a string with ms/sec/min/hour"
        self.__time *= (TimeTracker.__FORMATS[self.__format] / TimeTracker.__FORMATS[new_format])
        self.__format = new_format

    @verbose.getter
    def verbose(self):
        return self.__verbose

    @verbose.setter
    def verbose(self, value):
        assert isinstance(value, int) and value in (0, 1, 2), "verbose must be a int variable 0, 1 or 2"
        self.__verbose = value

    @rounding.getter
    def rounding(self):
        return self.__round

    @rounding.setter
    def rounding(self, value):
        assert isinstance(value, int) and value >= 1, "rounding must be a int variable >= 1"
        self.__round = value

    @stream.getter
    def stream(self):
        return str(self.__stream)

    @stream.setter
    def stream(self, stream):
        assert hasattr(stream, "write") and hasattr(stream.write, "__call__"), "stream must have write method"
        self.__stream = stream
