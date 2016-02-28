#!/usr/bin/env python
# encoding: utf-8

from ostn02python.OSGB import parse_grid, grid_to_ll
from ostn02python.OSTN02 import OSGB36_to_ETRS89
from nose.tools import assert_equal, assert_almost_equal
# from OSTN02 import *

def test_parse_grid1():
    xin, yin = parse_grid("ST", 00000, 00000)
    assert_equal((xin, yin), (300000, 100000))

def test_parse_grid2():
    xin, yin = parse_grid("NY", 46200, 75400)
    assert_equal((xin, yin), (346200, 575400))

def test_OSGB36_to_ETRS89():
    xin = 614300
    yin = 159900

    (x,y,h) = OSGB36_to_ETRS89(xin, yin)

    assert_equal((614199.522, 159979.837, 44.622), (x, y, h))

def test_grid_to_ll():
    x = 614199.522
    y = 159979.837 
    (gla, glo) = grid_to_ll(x, y)
    assert_almost_equal(gla, 51.297880, places=6)
    assert_almost_equal(glo, 1.072628, places=6)