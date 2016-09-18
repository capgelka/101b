#!/usr/bin/env python3

from collections.abc import Iterator, MutableSequence
from typing import Iterable, Generic, TypeVar, Union, Callable, Any, Optional
from itertools import chain, islice
from collections import deque
import re

T = TypeVar('T')


# class RingBuffer(MutableSequence):

#     def __init__(self, input_stream: Iterable[T] = [], bounds: Union[int, None] = None) -> None:
#         if bounds is None:
#             self._data = list(input_stream)
#         else:
#             self._data = []
#             for num, elem in enumerate(input_stream):
#                 self._data.append(elem)
#                 if num == bounds - 2:
#                     break
#         self.size = len(self._data)
#         self._start = 0

#     def __shifted(self, value: int) -> int:
#         return (self._start + value) % self.size

#     def __getitem__(self, num: int) -> T:
#         # print(self._data[self.__shifted(num)])
#         # print(self._start, num, self.size)
#         return self._data[self.__shifted(num)]

#     def insert(self, index: int, value: T) -> None:
#         self._data.insert(self.__shifted(index), value)
#         self.size += 1

#     def __delitem__(self, index: int) -> None:
#         del self._data[self.__shifted(index)]
#         self.size -= 1

#     def __len__(self) -> int:
#         return self.size

#     def __setitem__(self, key: int, value: T) -> None:
#         self._data[self.__shifted(key)] = value

#     def add_last(self, value: T) -> None:
#         self._data[self._start] = value
#         self._start += 1

#     def add_first(self, value: T) -> None:
#         self[self.size - 1] = value
#         print('call')
#         self._start = self._start - 1 if self._start > 0 else self.size


class LogFrame(object):

    def __init__(self, left_size: int, right_size: int, stream: Iterable[str]) -> None:
        self.left = deque(islice(stream, left_size), left_size)
        self.curr = next(iter(stream))
        self.right = deque(islice(stream, right_size), right_size)

    def show(self) -> None:
        print(*list(self.left),
              self.curr,
              *list(self.right),
              sep='\n')

    def shift(self, value: str) -> None:
        self.right.appendleft(self.curr)
        self.curr = self.left[-1]
        self.left.appendleft(value)

    def __iter__(self):
        return chain(self.left, (self.curr,), self.right)



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
        self.data.shift(next(self._input))
        return self.data


class LogFrameSearchStream(LogFrameStream):

    def __init__(self, 
                 logstream: Iterable[str],
                 predicate: Callable[[str], bool],
                 left_size: int = 100, 
                 right_size: int = 100) -> None:
        print(type(logstream))
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
            return self.data
        elif self._stopped:
            return None
        for _ in self:
            if self.predicate(self.data.curr):
                self.sucess = True
                self._stopped = True
                return self.data
        else:
            return None





            





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
