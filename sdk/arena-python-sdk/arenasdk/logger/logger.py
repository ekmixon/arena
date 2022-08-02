#!/usr/bin/env python
from __future__ import annotations
import os
import sys
from typing import List
from io import TextIOWrapper

class LoggerBuilder(object):
    def __init__(self):
        self._args = []
        self._accepter = sys.stdout 
    
    def with_accepter(self, accepter: TextIOWrapper) -> LoggerBuilder:
        self._accepter = accepter
        return self 
    
    def with_tail(self,tail: int) -> LoggerBuilder:
        if tail <= 0:
            return self
        self._args.append(f"--tail={tail}")
        return self
    
    def with_follow(self) -> LoggerBuilder:
        self._args.append("--follow")
        return self  
        
    def with_since_time(self,since_time: str) -> LoggerBuilder:
        self._args.append(f"--since-time={since_time}")
        return self 
    
    def with_since(self,since: str) -> LoggerBuilder:
        self._args.append(f"--since={since}")
        return self 

    def with_container(self,container: str) -> LoggerBuilder:
        self._args.append(f"--container={container}")
        return self 
    
    def get_args(self) -> List(str):
        return self._args
    
    def get_accepter(self):
        return self._accepter
        
        
    

        
