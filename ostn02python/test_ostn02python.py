#!/usr/bin/env python
# encoding: utf-8

from ostn02python.OSGB import parse_grid
from nose.tools import assert_equal
# from OSTN02 import *

def test_parse_grid1():
    xin, yin = parse_grid("ST", 00000, 00000)
    assert_equal((xin, yin), (300000, 100000))

def test_parse_grid2():
    xin, yin = parse_grid("NY", 46200, 75400)
    assert_equal((xin, yin), (346200, 575400))