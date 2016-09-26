#!/usr/bin/env python3

from collections.abc import Iterator, MutableSequence
from typing import Iterable, Generic, TypeVar, Union, Callable, Any, Optional
from itertools import chain, islice
from collections import deque


class LogFrame(object):

    def __init__(self, left_size: int, right_size: int, stream: Iterable[str]) -> None:
        size =  left_size + right_size + 1
        self.buff = deque(islice(stream, size), size)
        self._left = self._current = left_size
        self._right = right_size
        self.frozen_current = None

    def show(self) -> None:
        print('current:', self.current)
        print('all:')
        print(*self.buff, sep='\n')

    def shift(self, value: str) -> None:
        self.buff.append(value)

    @property
    def current(self):
        if self.frozen_current is not None:
            return self.frozen_current
        if len(self.buff) > self._current:
            index = self._current
        else:
            index = -1
        return self.buff[index]

    def fill_right_from_stream(self, stream: Iterable[str]) -> None:
        if not self.is_full():
            self.buff.extend(
                islice(stream, min(self.buff.maxlen - len(self.buff),
                                   self._right)))

    def is_full(self):
        return self.buff.maxlen == len(self.buff)

    def fix(self):
        self.frozen_current = self.current

    def __iter__(self):
        return iter(self.buff)



class LogFrameStream(Iterator):
    """Class to work with Log window"""
    def __init__(self, 
                 logstream: Iterable[str], 
                 left_size: int = 100, 
                 right_size: int = 100) -> None:
        super(LogFrameStream, self).__init__()
        self._input = iter(logstream)
        self.left_size = left_size
        self.right_size = right_size
        self.size = self.right_size + self.left_size + 1
        self.data = LogFrame(self.left_size, self.right_size, self._input)

    def __next__(self) -> LogFrame:
        try:
            self.data.shift(next(self._input))
        except StopIteration:
            if self.data._current != len(self.data.buff) and self.data.buff:
                self.data.buff.popleft()
            else:
                raise StopIteration
        return self.data


class LogFrameSearchStream(LogFrameStream):

    def __init__(self, 
                 logstream: Iterable[str],
                 predicate: Callable[[str], bool],
                 left_size: int = 100, 
                 right_size: int = 100) -> None:
        self.predicate = predicate
        super(LogFrameSearchStream, self).__init__([],
                                                   left_size, 
                                                   right_size)
        self._input = logstream
        self._stopped = False

    def __next__(self) -> LogFrame:
        if self._stopped:
            raise StopIteration
        return super(LogFrameSearchStream, self).__next__()

    def search(self) -> Optional[LogFrame]:
        if self._stopped:
            result = None
        else:
            try:
                result = next(frame for frame in self if self.predicate(frame.current))
                self.sucess = True
                result.fix()
            except StopIteration:
                result = None
            self.data.fill_right_from_stream(self._input)
            self._stopped = True
        return result



def search(stream: Iterable[str], id: Any) -> None:
    log_frame = LogFrameSearchStream(stream, lambda x: str(id) in x).search()
    if log_frame is None:
        print('No lines with specified mask found')
    else:
        log_frame.show()