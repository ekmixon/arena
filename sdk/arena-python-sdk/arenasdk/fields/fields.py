#!/usr/bin/env python
from abc import ABCMeta,abstractmethod
from arenasdk.exceptions.arena_exception import ArenaException
from arenasdk.enums.types import ArenaErrorType

class Field(object):
    __metaclass__ = ABCMeta  
    @abstractmethod
    def validate(self):
        pass  
      
    def options(self):
        pass  


class StringField(Field):
    def __init__(self,flag,value):
        super().__init__()
        self._flag = flag
        self._value = value
        
    def validate(self):
        if not self._flag or self._value == "":
            raise ArenaException(
                ArenaErrorType.ValidateArgsError,
                f"failed to validate flag {self._flag},value is null",
            )

        return True
    def options(self):
        return [f"{self._flag}={self._value}"]


class BoolField(Field):
    def __init__(self,flag):
        super().__init__()
        self._flag = flag

    def validate(self):
        return True 
    
    def options(self):
        return [self._flag]

class StringListField(Field):
    def __init__(self,flag,values):
        super().__init__()
        self._flag = flag
        self._values = values
        
    def validate(self):
        if not self._values or len(self._values) == 0:
            raise ArenaException(
                ArenaErrorType,
                f"failed to validate flag {self._flag},values are null",
            )

        return True
    
    def options(self):
        return [f"{self._flag}={value}" for value in self._values]

class StringMapField(Field):
    def __init__(self,flag,values,join_flag="="):
        super().__init__()
        self._flag = flag
        self._values = values
        self._join_flag = join_flag
    def validate(self):
        if not self._values or len(self._values) == 0:
            raise ArenaException(
                ArenaErrorType,
                f"failed to validate flag {self._flag},values are null",
            )

        return True
    def options(self):
        return [
            f"{self._flag}={key}{self._join_flag}{value}"
            for key, value in self._values.items()
        ] 