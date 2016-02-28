#!/usr/bin/env python
# encoding: utf-8

from ostn02python.OSGB import parse_grid, grid_to_ll
from ostn02python.OSTN02 import OSGB36_to_ETRS89

import six

def OSGB36GridRefToETRS89(mapRef):

	if len(mapRef) < 4:
		raise ValueError("Map ref too short")
	if len(mapRef) % 2 == 1:
		six.print_(ValueError("Unexpected input length"))

	coordLen = int((len(mapRef) - 2) / 2)
	code = mapRef[:2]
	east = int(mapRef[2:2+coordLen])*pow(10,5-coordLen)
	nrth = int(mapRef[2+coordLen:])*pow(10,5-coordLen)

	x1, y1 = parse_grid(code, east, nrth)

	(x,y,h) = OSGB36_to_ETRS89 (x1, y1)
	(gla, glo) = grid_to_ll(x, y)
	return (gla, glo)

