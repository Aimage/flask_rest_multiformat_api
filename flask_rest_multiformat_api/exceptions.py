# -*- coding: utf-8 -*-


class ApiException(Exception):
    errors = []
    
    def __init__(self, errors, code):
        self.errors = errors


