#!/usr/bin/env python
# encoding: utf-8

#OSTN02 for Python
#=================

#This is a port of the perl module Geo::Coordinates::OSTN02 by Toby Thurston (c) 2008
#Toby kindly allowed his code to be used for any purpose.
#The python port is (c) 2010-2011 Tim Sheerman-Chase
#The OSTN02 transform is Crown Copyright (C) 2002
#See COPYING for redistribution terms

import math

RAD = math.pi / 180
DAR = 180 / math.pi

WGS84_MAJOR_AXIS = 6378137.000
WGS84_FLATTENING = 1.0 / 298.257223563

# set defaults for Britain
ellipsoid_shapes = {
	'WGS84': [ 6378137.0000, 6356752.31425 ],
	'ETRS89' : [ 6378137.0000, 6356752.31425 ],
	'ETRN89' : [ 6378137.0000, 6356752.31425 ],
	'GRS80'  : [ 6378137.0000, 6356752.31425 ],
	'OSGB36' : [ 6377563.396,  6356256.910  ],
	'OSGM02' : [ 6377563.396,  6356256.910  ] }
# yes lots of synonyms

# constants for OSGB mercator projection
LAM0 = RAD * -2.0  # lon of grid origin
PHI0 = RAD * 49.0  # lat of grid origin
E0 =  400000   # Easting for origin
N0 = -100000   # Northing for origin
F0 = 0.9996012717 # Convergence factor

def ll_to_grid(lat,lon,alt=0.0,shape = 'WGS84'):

	#my $shape = defined $ellipsoid_shapes{$_[-1]} ? pop : 'OSGB36'; # last argument (or omitted)
	#if ($lat =~ $ISO_LL_Pattern ) {
	#	($lat, $lon, $alt) = parse_ISO_ll($lat);
	#}

	(a,b) = ellipsoid_shapes[shape]
	
	e2 = (a**2.-b**2.)/a**2.
	n = (a-b)/(a+b)
	
	phi = RAD * lat
	lam = RAD * lon

	sp2  = math.sin(phi)**2.
	nu   = a * F0 * (1. - e2 * sp2 ) ** -0.5
	rho  = a * F0 * (1. - e2) * (1. - e2 * sp2 ) ** -1.5
	eta2 = nu/rho - 1.
	
	M = _compute_M(phi, b, n)

	cp = math.cos(phi)
	sp = math.sin(phi)
	tp = math.tan(phi)
	tp2 = tp*tp
	tp4 = tp2*tp2

	I	= M + N0
	II   = nu/2.  * sp * cp
	III  = nu/24. * sp * cp**3. * (5.-tp2+9.*eta2)
	IIIA = nu/720.* sp * cp**5. *(61.-58.*tp2+tp4)

	IV   = nu*cp
	V	= nu/6.   * cp**3. * (nu/rho-tp2)
	VI   = nu/120. * cp**5. * (5.-18.*tp2+tp4+14.*eta2-58.*tp2*eta2)

	l = lam - LAM0
	north = I  + II*l**2. + III*l**4. + IIIA*l**6.;
	east  = E0 + IV*l	+   V*l**3. +   VI*l**5.;

	# round to 3dp (mm)
	#($east, $north) = map { sprintf "%.3f", $_ } ($east, $north);

	return (east,north)

def grid_to_ll(E,N,shape='WGS84'):

	#if ( $E =~ $GR_Pattern || $E =~ $Long_GR_Pattern || $E =~ $LR_Pattern ) {
	#	($E, $N) = parse_grid($E);
	#}

	(a,b) = ellipsoid_shapes[shape]

	e2 = (a**2.-b**2.)/a**2.
	n = (a-b)/(a+b)

	dN = N - N0

	phi = PHI0 + dN/(a * F0)

	M = _compute_M(phi, b, n);
	while (dN-M >= 0.001):
	   phi = phi + (dN-M)/(a * F0)
	   M = _compute_M(phi, b, n)

	sp2  = math.sin(phi)**2.;
	nu   = a * F0 *			 (1. - e2 * sp2 ) ** -0.5
	rho  = a * F0 * (1. - e2) * (1. - e2 * sp2 ) ** -1.5
	eta2 = nu/rho - 1.

	tp = math.tan(phi)
	tp2 = tp*tp
	tp4 = tp2*tp2

	VII  = tp /   (2.*rho*nu)
	VIII = tp /  (24.*rho*nu**3.) *  (5. +  3.*tp2 + eta2 - 9.*tp2*eta2)
	IX   = tp / (720.*rho*nu**5.) * (61. + 90.*tp2 + 45.*tp4)

	sp = 1.0 / math.cos(phi) 
	tp6 = tp4*tp2

	X	= sp/nu
	XI   = sp/(   6.*nu**3.)*(nu/rho + 2.*tp2)
	XII  = sp/( 120.*nu**5.)*(	  5. + 28.*tp2 +   24.*tp4)
	XIIA = sp/(5040.*nu**7.)*(	61. + 662.*tp2 + 1320.*tp4 + 720.*tp6)

	e = E - E0

	phi = phi		- VII*e**2. + VIII*e**4. -   IX*e**6.
	lam = LAM0 + X*e -  XI*e**3. +  XII*e**5. - XIIA*e**7.

	phi = phi * DAR
	lam = lam * DAR

	return (phi, lam)
	#return format_ll_ISO($phi,$lam);


def _compute_M(phi, b, n):
	p_plus  = phi + PHI0
	p_minus = phi - PHI0
	return b * F0 * (
		   (1 + n * (1 + 5./4*n*(1 + n)))*p_minus
		 - 3*n*(1+n*(1+7./8*n))  * math.sin(p_minus) * math.cos(p_plus)
		 + (15./8*n * (n*(1+n))) * math.sin(2*p_minus) * math.cos(2*p_plus)
		 - 35./24*n**3			 * math.sin(3*p_minus) * math.cos(3*p_plus)
		   )

Big_off = {#East then north
				 'G' : ( -1, 2 ),
				 'H' : ( 0, 2 ),
				 'J' : ( 1, 2 ),
				 'M' : ( -1, 1 ),
				 'N' : ( 0, 1 ),
				 'O' : ( 1, 1 ),
				 'R' : ( -1, 0 ),
				 'S' : ( 0, 0 ),
				 'T' : ( 1, 0 ),
		   }

Small_off = {#East then north
				 'A' : ( 0, 4 ),
				 'B' : ( 1, 4 ),
				 'C' : ( 2, 4 ),
				 'D' : ( 3, 4 ),
				 'E' : ( 4, 4 ),

				 'F' : ( 0, 3 ),
				 'G' : ( 1, 3 ),
				 'H' : ( 2, 3 ),
				 'J' : ( 3, 3 ),
				 'K' : ( 4, 3 ),

				 'L' : ( 0, 2 ),
				 'M' : ( 1, 2 ),
				 'N' : ( 2, 2 ),
				 'O' : ( 3, 2 ),
				 'P' : ( 4, 2 ),

				 'Q' : ( 0, 1 ),
				 'R' : ( 1, 1 ),
				 'S' : ( 2, 1 ),
				 'T' : ( 3, 1 ),
				 'U' : ( 4, 1 ),

				 'V' : ( 0, 0 ),
				 'W' : ( 1, 0 ),
				 'X' : ( 2, 0 ),
				 'Y' : ( 3, 0 ),
				 'Z' : ( 4, 0 ),
		   }

BIG_SQUARE = 500000
SQUARE	 = 100000
'''
# Landranger sheet data
# These are the full GRs (as metres from Newlyn) of the SW corner of each sheet.
our %LR = (
1   => [ 429000 ,1179000 ] ,
2   => [ 433000 ,1156000 ] ,
3   => [ 414000 ,1147000 ] ,
4   => [ 420000 ,1107000 ] ,
5   => [ 340000 ,1020000 ] ,
6   => [ 321000 , 996000 ] ,
7   => [ 315000 , 970000 ] ,
8   => [ 117000 , 926000 ] ,
9   => [ 212000 , 940000 ] ,
10  => [ 252000 , 940000 ] ,
11  => [ 292000 , 929000 ] ,
12  => [ 300000 , 939000 ] ,
13  => [  95000 , 903000 ] ,
14  => [ 105000 , 886000 ] ,
15  => [ 196000 , 900000 ] ,
16  => [ 236000 , 900000 ] ,
17  => [ 276000 , 900000 ] ,
18  => [  69000 , 863000 ] ,
19  => [ 174000 , 860000 ] ,
20  => [ 214000 , 860000 ] ,
21  => [ 254000 , 860000 ] ,
22  => [  57000 , 823000 ] ,
23  => [ 113000 , 836000 ] ,
24  => [ 150000 , 830000 ] ,
25  => [ 190000 , 820000 ] ,
26  => [ 230000 , 820000 ] ,
27  => [ 270000 , 830000 ] ,
28  => [ 310000 , 833000 ] ,
29  => [ 345000 , 830000 ] ,
30  => [ 377000 , 830000 ] ,
31  => [  50000 , 783000 ] ,
32  => [ 130000 , 800000 ] ,
33  => [ 170000 , 790000 ] ,
34  => [ 210000 , 780000 ] ,
35  => [ 250000 , 790000 ] ,
36  => [ 285000 , 793000 ] ,
37  => [ 325000 , 793000 ] ,
38  => [ 365000 , 790000 ] ,
39  => [ 120000 , 770000 ] ,
40  => [ 160000 , 760000 ] ,
41  => [ 200000 , 750000 ] ,
42  => [ 240000 , 750000 ] ,
43  => [ 280000 , 760000 ] ,
44  => [ 320000 , 760000 ] ,
45  => [ 360000 , 760000 ] ,
46  => [  92000 , 733000 ] ,
47  => [ 120000 , 732000 ] ,
48  => [ 120000 , 710000 ] ,
49  => [ 160000 , 720000 ] ,
50  => [ 200000 , 710000 ] ,
51  => [ 240000 , 720000 ] ,
52  => [ 270000 , 720000 ] ,
53  => [ 294000 , 720000 ] ,
54  => [ 334000 , 720000 ] ,
55  => [ 164000 , 680000 ] ,
56  => [ 204000 , 682000 ] ,
57  => [ 244000 , 682000 ] ,
58  => [ 284000 , 690000 ] ,
59  => [ 324000 , 690000 ] ,
60  => [ 110000 , 640000 ] ,
61  => [ 131000 , 662000 ] ,
62  => [ 160000 , 640000 ] ,
63  => [ 200000 , 642000 ] ,
64  => [ 240000 , 645000 ] ,
65  => [ 280000 , 650000 ] ,
66  => [ 316000 , 650000 ] ,
67  => [ 356000 , 650000 ] ,
68  => [ 157000 , 600000 ] ,
69  => [ 175000 , 613000 ] ,
70  => [ 215000 , 605000 ] ,
71  => [ 255000 , 605000 ] ,
72  => [ 280000 , 620000 ] ,
73  => [ 320000 , 620000 ] ,
74  => [ 357000 , 620000 ] ,
75  => [ 390000 , 620000 ] ,
76  => [ 195000 , 570000 ] ,
77  => [ 235000 , 570000 ] ,
78  => [ 275000 , 580000 ] ,
79  => [ 315000 , 580000 ] ,
80  => [ 355000 , 580000 ] ,
81  => [ 395000 , 580000 ] ,
82  => [ 195000 , 530000 ] ,
83  => [ 235000 , 530000 ] ,
84  => [ 265000 , 540000 ] ,
85  => [ 305000 , 540000 ] ,
86  => [ 345000 , 540000 ] ,
87  => [ 367000 , 540000 ] ,
88  => [ 407000 , 540000 ] ,
89  => [ 290000 , 500000 ] ,
90  => [ 317000 , 500000 ] ,
91  => [ 357000 , 500000 ] ,
92  => [ 380000 , 500000 ] ,
93  => [ 420000 , 500000 ] ,
94  => [ 460000 , 485000 ] ,
95  => [ 213000 , 465000 ] ,
96  => [ 303000 , 460000 ] ,
97  => [ 326000 , 460000 ] ,
98  => [ 366000 , 460000 ] ,
99  => [ 406000 , 460000 ] ,
100 => [ 446000 , 460000 ] ,
101 => [ 486000 , 460000 ] ,
102 => [ 326000 , 420000 ] ,
103 => [ 360000 , 420000 ] ,
104 => [ 400000 , 420000 ] ,
105 => [ 440000 , 420000 ] ,
106 => [ 463000 , 420000 ] ,
107 => [ 500000 , 420000 ] ,
108 => [ 320000 , 380000 ] ,
109 => [ 360000 , 380000 ] ,
110 => [ 400000 , 380000 ] ,
111 => [ 430000 , 380000 ] ,
112 => [ 470000 , 385000 ] ,
113 => [ 510000 , 386000 ] ,
114 => [ 220000 , 360000 ] ,
115 => [ 240000 , 345000 ] ,
116 => [ 280000 , 345000 ] ,
117 => [ 320000 , 340000 ] ,
118 => [ 360000 , 340000 ] ,
119 => [ 400000 , 340000 ] ,
120 => [ 440000 , 350000 ] ,
121 => [ 478000 , 350000 ] ,
122 => [ 518000 , 350000 ] ,
123 => [ 210000 , 320000 ] ,
124 => [ 250000 , 305000 ] ,
125 => [ 280000 , 305000 ] ,
126 => [ 320000 , 300000 ] ,
127 => [ 360000 , 300000 ] ,
128 => [ 400000 , 308000 ] ,
129 => [ 440000 , 310000 ] ,
130 => [ 480000 , 310000 ] ,
131 => [ 520000 , 310000 ] ,
132 => [ 560000 , 310000 ] ,
133 => [ 600000 , 310000 ] ,
134 => [ 617000 , 290000 ] ,
135 => [ 250000 , 265000 ] ,
136 => [ 280000 , 265000 ] ,
137 => [ 320000 , 260000 ] ,
138 => [ 345000 , 260000 ] ,
139 => [ 385000 , 268000 ] ,
140 => [ 425000 , 270000 ] ,
141 => [ 465000 , 270000 ] ,
142 => [ 504000 , 274000 ] ,
143 => [ 537000 , 274000 ] ,
144 => [ 577000 , 270000 ] ,
145 => [ 200000 , 220000 ] ,
146 => [ 240000 , 225000 ] ,
147 => [ 270000 , 240000 ] ,
148 => [ 310000 , 240000 ] ,
149 => [ 333000 , 228000 ] ,
150 => [ 373000 , 228000 ] ,
151 => [ 413000 , 230000 ] ,
152 => [ 453000 , 230000 ] ,
153 => [ 493000 , 234000 ] ,
154 => [ 533000 , 234000 ] ,
155 => [ 573000 , 234000 ] ,
156 => [ 613000 , 250000 ] ,
157 => [ 165000 , 201000 ] ,
158 => [ 189000 , 190000 ] ,
159 => [ 229000 , 185000 ] ,
160 => [ 269000 , 205000 ] ,
161 => [ 309000 , 205000 ] ,
162 => [ 349000 , 188000 ] ,
163 => [ 389000 , 190000 ] ,
164 => [ 429000 , 190000 ] ,
165 => [ 460000 , 195000 ] ,
166 => [ 500000 , 194000 ] ,
167 => [ 540000 , 194000 ] ,
168 => [ 580000 , 194000 ] ,
169 => [ 607000 , 210000 ] ,
170 => [ 269000 , 165000 ] ,
171 => [ 309000 , 165000 ] ,
172 => [ 340000 , 155000 ] ,
173 => [ 380000 , 155000 ] ,
174 => [ 420000 , 155000 ] ,
175 => [ 460000 , 155000 ] ,
176 => [ 495000 , 160000 ] ,
177 => [ 530000 , 160000 ] ,
178 => [ 565000 , 155000 ] ,
179 => [ 603000 , 133000 ] ,
180 => [ 240000 , 112000 ] ,
181 => [ 280000 , 112000 ] ,
182 => [ 320000 , 130000 ] ,
183 => [ 349000 , 115000 ] ,
184 => [ 389000 , 115000 ] ,
185 => [ 426000 , 116000 ] ,
186 => [ 465000 , 125000 ] ,
187 => [ 505000 , 125000 ] ,
188 => [ 545000 , 125000 ] ,
189 => [ 585000 , 115000 ] ,
190 => [ 207000 ,  87000 ] ,
191 => [ 247000 ,  72000 ] ,
192 => [ 287000 ,  72000 ] ,
193 => [ 310000 ,  90000 ] ,
194 => [ 349000 ,  75000 ] ,
195 => [ 389000 ,  75000 ] ,
196 => [ 429000 ,  76000 ] ,
197 => [ 469000 ,  90000 ] ,
198 => [ 509000 ,  97000 ] ,
199 => [ 549000 ,  94000 ] ,
200 => [ 175000 ,  50000 ] ,
201 => [ 215000 ,  47000 ] ,
202 => [ 255000 ,  32000 ] ,
203 => [ 132000 ,  11000 ] ,
204 => [ 172000 ,  14000 ] ,
);

'''

def parse_grid (letters,e=0.0,n=0.0):
	"""Convert from OS grid references with letter prefix to the national grid.
	e and n are in metres.
	e.g. OSGB.parse_grid("ST", 00000, 00000) converts to (300000, 100000)
	NY462754 is OSGB.parse_grid("NY", 46200, 75400) and converts to (346200, 575400)
	"""

	letters = str.upper(letters)

	c = letters[0:1].upper()
	e += Big_off[c][0]*BIG_SQUARE
	n += Big_off[c][1]*BIG_SQUARE
	
	d = letters[1:2].upper()
	e += Small_off[d][0]*SQUARE
	n += Small_off[d][1]*SQUARE

	return (e, n)

def grid_to_small_code(e, n):
	er = int(e % BIG_SQUARE) / SQUARE
	nr = int(n % BIG_SQUARE) / SQUARE
	found = None
	for cd in Small_off:
		if er == Small_off[cd][0] and nr == Small_off[cd][1]:
			found = cd
	ebig = e - er *  SQUARE
	nbig = n - nr *  SQUARE
	return found, ebig, nbig

def grid_to_big_code(e, n):
	found = None
	for cd in Big_off:
		if e == Big_off[cd][0] and n == Big_off[cd][1]:
			found = cd
	return found

def os_streetview_tile_to_grid(tile_name):
	#Convert OS Street View tile name (e.g. SO02NW) to grid (e.g. 
	e,n = parse_grid(tile_name)
	e += 10000 * int(tile_name[2:3])
	n += 10000 * int(tile_name[3:4])
	
	if tile_name[4:6].upper() == "NW": 
		n += 5000
	if tile_name[4:6].upper() == "NE": 
		n += 5000
		e += 5000
	if tile_name[4:6].upper() == "SE": 
		e += 5000
	return e, n

def grid_to_os_streetview_tile(grid):

	e = grid[0]
	n = grid[1]

	#Deal with small offsets
	e, eSmall = divmod(e, 5000)
	n, nSmall = divmod(n, 5000)
	e = int(e * 5000)
	n = int(n * 5000)

	#Find which corner of the tile we are in
	eRem = e % 10000
	nRem = n % 10000
	if eRem >= 5000.: 
		etile = True
		e -= 5000
	else: etile = False
	if nRem >= 5000.: 
		ntile = True
		n -= 5000
	else: ntile = False
	corner = None
	if etile and ntile: corner = "NE"
	if etile and not ntile: corner = "SE"
	if not etile and ntile: corner = "NW"
	if not etile and not ntile: corner = "SW"

	#Mid level offset
	eMidOffset = int(e % 100000) / 10000
	nMidOffset = int(n % 100000) / 10000
	e -= eMidOffset * 10000
	n -= nMidOffset * 10000

	smallCode, e, n = grid_to_small_code(e, n)
	bigCode = grid_to_big_code(e / BIG_SQUARE, n / BIG_SQUARE)

	codeOut = "{0}{1}{2}{3}{4}".format(bigCode, smallCode, eMidOffset, nMidOffset, corner)
	return codeOut, eSmall, nSmall

