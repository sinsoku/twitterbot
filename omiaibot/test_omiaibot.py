#!/usr/bin/env python
# -*- coding:utf-8 -*-
from webtest import TestApp
from main import application

app = TestApp(application())

def test_MainPage():
    response = app.get('/omiaibot/')
    assert 'Hello, World' in str(response)
