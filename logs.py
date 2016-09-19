#!/usr/bin/env python3

from collections.abc import Iterator, MutableSequence
from typing import Iterable, Generic, TypeVar, Union, Callable, Any, Optional
from itertools import chain, islice
from collections import deque
import re

T = TypeVar('T')


class LogFrame(object):

    def __init__(self, left_size: int, right_size: int, stream: Iterable[str]) -> None:
        size =  left_size + right_size + 1
        self.buff = deque(islice(stream, size), size)
        self._current = left_size
        # self.left = deque(islice(stream, left_size), left_size)
        # self.curr = next(iter(stream))
        # self.right = deque(islice(stream, right_size), right_size)

    def show(self) -> None:
        print(*self.buff)

    def shift(self, value: str) -> None:
        self.buff.append(value)

    @property
    def current(self):
        return self.buff[self._current]

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
            if self.data._current != len(self.data.buff):
                self.data.buff.popleft()
            else:
                raise StopIteration
            # self.data.buff.rotate(1)
        return self.data


class LogFrameSearchStream(LogFrameStream):

    def __init__(self, 
                 logstream: Iterable[str],
                 predicate: Callable[[str], bool],
                 left_size: int = 100, 
                 right_size: int = 100) -> None:
        # print(type(logstream))
        first = list(islice(logstream, left_size + right_size + 1))
        found = [(n, x) for (n, x) in enumerate(first) if predicate(x)]
        if len(found) > 1:
            raise KeyError('There are more then one string '
                           'satisfies the predicate: {}'.format("\n".join(x[1] for x in found)))
        super(LogFrameSearchStream, self).__init__(logstream if not found else [], 
                                                   left_size, 
                                                   right_size)
        self.predicate = predicate
        if found:
            result_number = found[0][0]
            self.sucess = True
            if self.left_size < result_number:
                self.data = LogFrame(self.left_size, self.right_size, 
                                     chain(first[result_number - self.left_size:], 
                                           self._input))
            if self.left_size > result_number:
                self.data = LogFrame(result_number, 
                                     self.right_size,
                                     first[:result_number + self.right_size])
            self._stopped = True
        else:
            self.sucess = False
            self._stopped = False

    def __next__(self) -> LogFrame:
        if self._stopped:
            raise StopIteration
        return super(LogFrameSearchStream, self).__next__()

    def search(self) -> Optional[LogFrame]:
        if self.sucess:
            result = self.data
            # return self.data
        elif self._stopped:
            result = None
            # return None
        else:
            try:
                result = next(frame for frame in self if self.predicate(frame.current))
                self.sucess = True
            except StopIteration:
                result = None
            self._stopped = True
        return result
        # return next(filter(lambda frame: self.predicate(frame.current), self))
        # for _ in self:
        #     if self.predicate(self.data.current):
        #         self.sucess = True
        #         self._stopped = True
        #         return self.data
        # else:
        #     return None





            





def search(stream: Iterable[str], id: Any) -> None:
    log_frame = LogFrameSearchStream(stream, lambda x: str(id) in x).search()
    if log_frame is None:
        print('No lines with specified mask found')
    else:
        log_frame.show()

    # log.
    # first = next(stream)
    # if x in first.left:
    #     return first
    # try:
    #     result = next(frame for frame in stream if)
    # except Exception, e:
    #     raise
    # else:
    #     pass
    # finally:
    #     pass

if __name__ == '__main__':
    import sys
    # buff = RingBuffer('abcde', None)
    # print(buff)
    # for i in buff:
    #     print(i)
    # clone = list(buff)
    # for b in reversed(clone):
    #     buff.add_first(b)
    #     print(buff)
    #     print(clone)
    #     print('-----------')
    with open('../../.mcabber/histo/{}'.format(sys.argv[1]), 'r') as f:
        search(f.readlines(), sys.argv[2])
