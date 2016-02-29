OSTN02 for Python
=================

This is a port of the perl module Geo::Coordinates::OSTN02 by Toby Thurston (c) 2008. See example.py for typical coordinate transforms.

Toby kindly allowed his code to be used for any purpose.

The python port for v2.7 and v3.0+ is (c) 2010-2015 Tim Sheerman-Chase

The OSTN02 transform is Crown Copyright (C) 2002

See COPYING for redistribution terms (BSD license)

The documentation for the original Perl module, by Toby Thurston is shown below, this should be modified to reflect the Python code.

# Geo::Coordinates::OSGB - Convert coordinates between Lat/Lon and the British National Grid

An implementation of co-ordinate conversion for England, Wales, and Scotland
based on formulae published by the Ordnance Survey of Great Britain.

These modules will convert accurately between an OSGB national grid
reference and lat/lon coordinates based on the OSGB geoid model.  (For an
explanation of what a geoid model is and why you should care, read the
L<Theory> section below.) The OSGB geoid model fits mainland Britain very
well, but is rather different from the international WGS84 model that has
rapidly become the de facto universal standard model thanks to the
popularity of GPS devices and maps on the Internet.  So, if you are trying
to translate from an OSGB grid reference to lat/lon coordinates that can be
used in Google Earth, Wikipedia, or some other Internet based tool, you will
need to do two transformations:  first translate your grid ref into OSGB
lat/lon; then nudge the result into WGS84.  Routines are provided to do both
of these operations, but they are only approximate.  The inaccuracy of the
approximation varies according to where you are in the country but may be as
much as several metres in some areas.

To get more accurate results you need to combine this module with its
companion L<Geo::Coordinates::OSTN02> which implements the transformation
that now defines the relationship between GPS survey data based on WGS84 and
the British National Grid.  Using this module you should be able to get
results that are accurate to within a few centimetres, but it is slightly
slower and requires more memory to run.

Note that the OSGB (and therefore this module) does not cover the whole of
the British Isles, nor even the whole of the UK, in particular it covers
neither the Channel Islands nor Northern Ireland.  The coverage that is
included is essentially the same as the coverage provided by the OSGB
"Landranger" 1:50000 series maps.

## SYNOPSIS

  use Geo::Coordinates::OSGB qw(ll_to_grid grid_to_ll);

  # Basic conversion routines
  ($easting,$northing) = ll_to_grid($lat,$lon);
  ($lat,$lon) = grid_to_ll($easting,$northing);

## DESCRIPTION

These modules provide a collection of routines to convert between coordinates expressed as latitude & longtitude and
map grid references, using the formulae given in the British Ordnance Survey's excellent information leaflet, referenced
below in L<Theory>.  There are some key concepts explained in that section that you need to know in order to use these
modules successfully, so you are recommended to at least skim through it now.

The module is implemented purely in Perl, and should run on any Perl platform.

In this description `OS' means `the Ordnance Survey of Great Britain': the British
government agency that produces the standard maps of England, Wales, and
Scotland.  Any mention of `sheets' or `maps' refers to one or more of the 204
sheets in the 1:50,000 scale `Landranger' series of OS maps.

This code is fine tuned to the British national grid system.  You could use it
elsewhere but you would need to adapt it.  Some starting points for doing this
are explained in the L<Theory> section below.


## FUNCTIONS

The following functions can be exported from the C<Geo::Coordinates::OSGB>
module:

    grid_to_ll                ll_to_grid

    shift_ll_into_WGS84      shift_ll_from_WGS84

    parse_grid
    parse_trad_grid          format_grid_trad
    parse_GPS_grid            format_grid_GPS
    parse_landranger_grid      format_grid_landranger

    parse_ISO_ll                format_ll_trad
                                format_ll_ISO

None of these is exported by default, so pick the ones you want or use an C<:all> tag to import them all at once.

  use Geo::Coordinates::OSGB ':all';

=over 4

=item ll_to_grid(lat,lon)

When called in a void context, or with no arguments C<ll_to_grid> does nothing.

When called in a list context, C<ll_to_grid> returns two numbers that represent
the easting and the northing corresponding to the latitude and longitude
supplied.

The parameters can be supplied as real numbers representing decimal degrees, like this

    my ($e,$n) = ll_to_grid(51.5, 2.1);

Following the normal convention, positive numbers mean North or East, negative South or West.
If you have data with degrees, minutes and seconds, you can convert them to decimals like this:

    my ($e,$n) = ll_to_grid(51+25/60, 0-5/60-2/3600);

Or you can use a single string in ISO 6709 form, like this:

    my ($e,$n) = ll_to_grid('+5130-00005/');

To learn exactly what is matched by this last option, read the source of the module and look for the
definition of C<$ISO_LL_Pattern>.  Note that the neither the C<+> or C<-> signs at the
beginning and in the middle, nor the trailing C</> may be omitted.

If you have trouble remembering the order of the arguments, note that
latitude comes before longitude in the alphabet too.

The easting and northing will be returned as a whole number of metres from
the point of origin of the British Grid (which is a point a little way to the
south-west of the Scilly Isles).

If you want the result presented in a more traditional grid reference format you should pass the results to one of the
grid formatting routines, which are described below.  Like this.

    $gridref = format_grid_trad(ll_to_grid(51.5,-0.0833));
    $gridref = format_grid_GPS(ll_to_grid(51.5,-0.0833));
    $gridref = format_grid_landranger(ll_to_grid(51.5,-0.0833));

However if you call C<ll_to_grid> in a scalar context, it will
automatically call C<format_grid_trad> for you.

It is not needed for any normal work, but C<ll_to_grid()> also takes an
optional argument that sets the ellipsoid model to use.  This normally
defaults to `OSGB36', the name of the normal model for working with British
maps.  If you are working with the highly accurate OSTN02 conversions
supplied in the companion module in this distribution, then you will need to
produce pseudo-grid references as input to those routines.  For these
purposes you should call C<ll_to_grid()> like this:

    my $pseudo_gridref = ll_to_grid(51.2, -0.4, 'WGS84');

and then transform this to a real grid reference using C<ETRS89_to_OSGB36()>
from the companion module.  This is explained in more detail below.

=item format_grid_trad(e,n)

Formats an (easting, northing) pair into traditional `full national grid
reference' with two letters and two sets of three numbers, like this
`TQ 102 606'.  If you want to remove the spaces, just apply `C<s/\s//g>` to it.

    $gridref = format_grid_trad(533000, 180000); # TQ 330 800
    $gridref =~ s/\s//g;                         # TQ330800

If you want the individual components call it in a list context.

    ($sq, $e, $n) = format_grid_trad(533000, 180000); # (TQ,330,800)

Note the easting and northing are truncated to hectometers (as the OS system
demands), so the grid reference refers to the lower left corner of the
relevant 100m square.

=item format_grid_GPS(e,n)

Users who have bought a GPS receiver may initially have been puzzled by the
unfamiliar format used to present coordinates in the British national grid format.
On my Garmin Legend C it shows this sort of thing in the display.

    TQ 23918
   bng 00972

and in the track logs the references look like this C<TQ 23918 00972>.

These are just the same as the references described on the OS sheets, except
that the units are metres rather than hectometres, so you get five digits in
each of the easting and northings instead of three.  So in a scalar context
C<format_grid_GPS()> returns a string like this:

    $gridref = format_grid_GPS(533000, 180000); # TQ 33000 80000

If you call it in a list context, you will get a list of square, easting, and northing, with the easting and northing as
metres within the grid square.

    ($sq, $e, $n) = format_grid_GPS(533000, 180000); # (TQ,33000,80000)

Note that, at least until WAAS is working in Europe, the results from your
GPS are unlikely to be more accurate than plus or minus 5m even with perfect
reception.  Most GPS devices can display the accuracy of the current fix you
are getting, but you should be aware that all normal consumer-level GPS
devices can only ever produce an approximation of an OS grid reference, no
matter what level of accuracy they may display.  The reasons for this are
discussed below in the section on L<Theory>.

=item format_grid_landranger(e,n)

This routine does the same as C<format_grid_trad>, but it appends the number of the relevant OS Landranger 1:50,000
scale map to the traditional grid reference.  Note that there may be several or no sheets returned.  This is because
many (most) of the Landranger sheets overlap, and many other valid grid references are not on any of the sheets (because
they are in the sea or a remote island.  This module does not yet cope with the detached insets on some sheets.

In a list context you will get back a list like this:  (square, easting,
northing, sheet) or (square, easting, northing, sheet1, sheet2) etc.  There
are a few places where three sheets overlap, and one corner of Herefordshire
which appears on four maps (sheets 137, 138, 148, and 149).  If the GR is not
on any sheet, then the list of sheets will be empty.

In a scalar context you will get back the same information in a helpful
string form like this "NN 241 738 on OS Sheet 44".  Note that the easting and
northing will have been truncated to the normal hectometre three
digit form.  The idea is that you'll use this form for people who might actually
want to look up the grid reference on the given map sheet, and the traditional
GR form is quite enough accuracy for that purpose.

=item parse_trad_grid(grid_ref)

Turns a traditional grid reference into a full easting and northing pair in
metres from the point of origin.  The I<grid_ref> can be a string like
C<'TQ203604'> or C<'SW 452 004'>, or a list like this C<('TV', '435904')> or a list
like this C<('NN', '345', '208')>.


=item parse_GPS_grid(grid_ref)

Does the same as C<parse_trad_grid> but is looking for five digit numbers
like C<'SW 45202 00421'>, or a list like this C<('NN', '34592', '20804')>.

=item parse_landranger_grid(sheet, e, n)

This converts an OS Landranger sheet number and a local grid reference
into a full easting and northing pair in metres from the point of origin.

The OS Landranger sheet number should be between 1 and 204 inclusive (but
I may extend this when I support insets).  You can supply C<(e,n)> as 3-digit
hectometre numbers or 5-digit metre numbers.  In either case if you supply
any leading zeros you should 'quote' the numbers to stop Perl thinking that
they are octal constants.

This module will croak at you if you give it an undefined sheet number, or
if the grid reference that you supply does not exist on the sheet.

In order to get just the coordinates of the SW corner of the sheet, just call
it with the sheet number.  It is easy to work out the coordinates of the
other corners, because all OS Landranger maps cover a 40km square (if you
don't count insets or the occasional sheet that includes extra details
outside the formal margin).

=item parse_grid(grid_ref)

Attempts to match a grid reference some form or other
in the input string and will then call the appropriate grid
parsing routine from those defined above.  In particular it will parse strings in the form
C<'176-345210'> meaning grid ref 345 210 on sheet 176, as well as C<'TQ345210'> and C<'TQ 34500 21000'> etc.

=item grid_to_ll(e,n) or grid_to_ll(grid_ref)

When called in list context C<grid_to_ll()> returns a pair of numbers
representing longitude and latitude coordinates, as real numbers.  Following
convention, positive numbers are North and East, negative numbers are South
and West.  The fractional parts of the results represent fractions of
degrees.

When called in scalar context it returns a string in ISO longitude and latitude
form, such as C<'+5025-00403/'> with the result rounded to the nearest minute (the
formulae are not much more accurate than this).  In a void context it does
nothing.

The arguments must be an (easting, northing) pair representing the absolute grid reference in metres from the point of
origin.  You can get these from a grid reference string by calling C<parse_grid()> first.

An optional last argument defines the geoid model to use just as it does for C<ll_to_grid()>.  This is only necessary is
you are working with the pseudo-grid references produced by the OSTN02 routines.  See L<Theory> for more discussion.

=item format_ll_trad(lat, lon)

Takes latitude and longitude in decimal degrees as arguments and returns a string like this

    N52:12:34 W002:30:27

In a list context it returns all 8 elements (hemisphere, degrees, minutes, seconds for each of lat and lon) in a list.
In a void context it does nothing.

=item format_ll_ISO(lat, lon)

Takes latitude and longitude in decimal degrees as arguments and returns a string like this

    +5212-00230/

In a list context it returns all 6 elements (sign, degrees, minutes for each of lat and lon) in a list.
In a void context it does nothing.


=item parse_ISO_ll(ISO_string)

Reads an ISO 6709 formatted location identifier string such as '+5212-00230/'.
To learn exactly what is matched by this last option, read the source of the module and look for the
definition of C<$ISO_LL_Pattern>.  Note that the neither the C<+> or C<-> signs at the
beginning and in the middle, nor the trailing C</> may be omitted.  These strings can also include
the altitude of a point, in metres, like this: '+5212-00230+140/'.  If you omit the altitude, 0 is assumed.

In a list context it returns ($lat, $lon, $altitude).  So if you don't want or don't need the altitude, you should just
drop it, for example like this:

   my ($lat, $lon) = parse_ISO_ll('+5212-00230/')

In normal use you won't notice this.  In particular you don't need to worry about it when
passing the results on to C<ll_to_grid>, as that routine looks for an optional altitude after the lat/lon.

=item shift_ll_from_WGS84(lat, lon, altitude)

Takes latitude and longitude in decimal degrees (plus an optional altitude in metres) from a WGS84 source (such as your
GPS handset or Google Earth) and returns an approximate equivalent latitude and longitude according to the OSGM02 model.
To determine the OSGB grid reference for given WGS84 lat/lon coordinates, you should call this before
you call C<ll_to_grid>.  Like so:

  ($lat, $lon, $alt) = shift_ll_from_WGS84($lat, $lon, $alt);
  ($e, $n) = ll_to_grid($lat,$lon);

You don't need to call this to determine a grid reference from lat/lon coordinates printed on OSGB maps (the so called
"graticule intersections" marked in pale blue on the Landranger series).

This routine provide a fast approximation; for a slower, more accurate approximation use the companion
L<Geo::Coordinates::OSTN02> modules.

=item shift_ll_into_WGS84(lat, lon, altitude)

Takes latitude and longitude in decimal degrees (plus an optional altitude in metres) from an OSGB source (such as
coordinates you read from a Landranger map, or more likely coordinates returned from C<grid_to_ll()>) and adjusts them
to fit the WGS84 model.

To determine WGS84 lat/lon coordinates (for use in Wikipedia, or Google Earth etc) for a given OSGB grid
reference, you should call this after you call C<grid_to_ll()>.  Like so:

  ($lat, $lon) = grid_to_ll($e, $n);
  ($lat, $lon, $alt) = shift_ll_into_WGS84($lat, $lon, $alt);

This routine provide a fast approximation; for a slower, more accurate approximation use the companion
L<Geo::Coordinates::OSTN02> modules.

=back

## THEORY

The algorithms and theory for these conversion routines are all from
I<A Guide to Coordinate Systems in Great Britain>
published by the OSGB, April 1999 and available at
http://www.ordnancesurvey.co.uk/oswebsite/gps/information/index.html

You may also like to read some of the other introductory material there.
Should you be hoping to adapt this code to your own custom Mercator
projection, you will find the paper called I<Surveying with the
National GPS Network>, especially useful.

The routines are intended for use in Britain with the Ordnance Survey's
National Grid, however they are written in an entirely generic way, so that
you could adapt them to any other ellipsoid model that is suitable for your
local area of the earth.   There are other modules that already do this that
may be more suitable (which are referenced in the L<See Also> section), but
the key parameters are all defined at the top of the module.

    $ellipsoid_shapes{OSGB36} = [ 6377563.396,  6356256.910  ];
    use constant LAM0 => RAD * -2;  # lon of grid origin
    use constant PHI0 => RAD * 49;  # lat of grid origin
    use constant E0   =>  400000;   # Easting for origin
    use constant N0   => -100000;   # Northing for origin
    use constant F0   => 0.9996012717; # Convergence factor

The ellipsoid model is defined by two numbers that represent the major and
minor radius measured in metres.  The Mercator grid projection is then
defined by the other five parameters.  The general idea is that you pick a
suitable point to start the grid that minimizes the inevitable distortion
that is involved in a Mercator projection from spherical to Euclidean
coordinates.  Such a point should be on a meridian that bisects the area of
interest and is nearer to the equator than the whole area.  So for Britain
the point of origin is 2degW and 49degN (in the OSGB geoid model) which is near
the Channel Islands.  This point should be set as the C<LAM0> and C<PHI0>
parameters (as above) measured in radians.  Having this True Point of Origin
in the middle and below (or above if you are antipodean) minimizes
distortion but means that some of the grid values would be negative unless
you then also adjust the grid to make sure you do not get any negative
values in normal use.  This is done by defining the grid coordinates of the
True Point of Origin to be such that all the coordinates in the area of
interest will be positive.  These are the parameters C<E0> and C<N0>.
For Britain the coordinates are set as 400000 and -100000, so the that point
(0,0) in the grid is just to the south west of the Scilly Isles.  This (0,0)
point is called the False Point of Origin.  The fifth parameter affects the
convergence of the Mercator projection as you get nearer the pole; this is
another feature designed to minimize distortion, and if in doubt set it to
1 (which means it has no effect).  For Britain, being so northerly it is set
to slightly less than 1.

## The British National Grid

One consequence of the True Point of Origin of the British Grid being set to
C<+4900-00200/> is that all the vertical grid lines are parallel to the 2degW
meridian; you can see this on the appropriate OS maps (for example
Landranger sheet 184), or on the C<plotmaps.pdf> picture supplied with this
package.  The effect of moving the False Point of Origin to the far south
west is that all grid references always positive.

Strictly grid references are given as whole numbers of metres from this
point, with the easting always given before the northing.  For everyday use
however, the OSGB suggest that grid references need only to be given within
the local 100km square as this makes the numbers smaller.  For this purpose
they divide Britain into a series of 100km squares identified in pair of
letters:  TQ, SU, ND, etc.  The grid of the big squares actually used is
something like this:

                               HP
                               HU
                            HY
                   NA NB NC ND
                   NF NG NH NJ NK
                   NL NM NN NO NP
                      NR NS NT NU
                      NW NX NY NZ
                         SC SD SE TA
                         SH SJ SK TF TG
                      SM SN SO SP TL TM
                      SR SS ST SU TQ TR
                   SV SW SX SY SZ TV

SW covers most of Cornwall, TQ London, and HU the Shetlands.  Note that it
has the neat feature that N and S are directly above each other, so that
most Sx squares are in the south and most Nx squares are in the north.

Within each of these large squares, we only need five digit coordinates ---
from (0,0) to (99999,99999) --- to refer to a given square metre.  For daily
use however we don't generally need such precision, so the normal
recommended usage is to use units of 100m (hectometres) so that we only need
three digits for each easting and northing --- 000,000 to 999,999.  If we
combine the easting and northing we get the familiar traditional six figure
grid reference.  Each of these grid references is repeated in each of the
large 100km squares but for local use with a particular map, this does not
usually matter.  Where it does matter, the OS suggest that the six figure
reference is prefixed with the identifier of the large grid square to give a
`full national grid reference', such as TQ330800.  This system is described
in the notes of in the corner of every Landranger 1:50,000 scale map.

Modern GPS receivers can all display coordinates in the OS grid system.  You
just need to set the display units to be `British National Grid' or whatever
similar name is used on your unit.  Most units display the coordinates as two
groups of five digits and a grid square identifier.  The units are metres within
the grid square (although beware that the GPS fix is unlikely to be accurate down
to the last metre).


## Geoid models

This section explains the fundamental problems of mapping a spherical earth
onto a flat piece of paper (or computer screen).  A basic understanding of
this material will help you use these routines more effectively.  It will
also provide you with a good store of ammunition if you ever get into an
argument with someone from the Flat Earth Society.

It is a direct consequence of Newton's law of universal gravitation (and in
particular the bit that states that the gravitational attraction between two
objects varies inversely as the square of the distance between them) that all
planets are roughly spherical.  (If they were any other shape gravity would
tend to pull them into a sphere).  On the other hand, most useful surfaces
for displaying large scale maps (such as pieces of paper or screens) are
flat.  There is therefore a fundamental problem in making any maps of the
earth that its curved surface being mapped must be distorted at least
slightly in order to get it to fit onto the flat map.

This module sets out to solve the corresponding problem of converting
latitude and longitude coordinates (designed for a spherical surface) to and
from a rectangular grid (for a flat surface).  This projection is in itself
is a fairly lengthy bit of maths, but what makes it extra complicated is
that the earth is not quite a sphere.  Because our planet spins about a
vertical axis, it tends to bulge out slightly in the middle, so it is more
of an oblate spheroid than a sphere.  This makes the maths even longer, but
the real problem is that the earth is not a regular oblate spheroid either,
but an irregular lump that closely resembles an oblate spheroid and which is
constantly (if slowly) being rearranged by plate tectonics.  So the best we
can do is to pick an imaginary regular oblate spheroid that provides a good
fit for the region of the earth that we are interested in mapping.  The
British Ordnance Survey did this back in 1830 and have used it ever since as
the base on which the National Grid for Great Britain is constructed.  You
can also call an oblate spheroid an ellipsoid if you like.  The general term
for an ellipsoid model of the earth is a "geoid".

The first standard OSGB geoid is known as "Airy 1830" after the year of its
first development.  It was revised in 1936, and that version, generally
known as OSGB36, is the basis of all current OSGB mapping.  In 2002 the
model was redefined (but not functionally changed) as a transformation from
the international geoid model WGS84.  This redefinition is called OSGM02.
For the purposes of these modules (and most other purposes) OSGB36 and
OSGM02 may be treated as synonyms.

The general idea is that you can establish your latitude and longitude by
careful observation of the sun, the moon, the planets, or your GPS handset,
and that you then do some clever maths to work out the corresponding grid
reference using a suitable geoid.  These modules let you do the clever
maths, and the geoid they use is the OSGM02 one.  This model provides a good
match to the local shape of the Earth in the British Isles, but is not
designed for use in the rest of the world; there are many other models in
use in other countries.

In the mid-1980s a new standard geoid model was defined to use with the
fledgling global positioning system (GPS).  This model is known as WGS84, and
is designed to be a compromise model that works equally well for all parts of
the globe (or equally poorly depending on your point of view --- for one
thing WGS84 defines the Greenwich observatory in London to be not quite on
the 0deg meridian).  Nevertheless WGS84 has grown in importance as GPS systems
have become consumer items and useful global mapping tools (such as Google
Earth) have become freely available through the Internet.  Most latitude and
longitude coordinates quoted on the Internet (for example in Wikipedia) are
WGS84 coordinates.

One thing that should be clear from the theory is that there is no such
thing as a single definitive set of coordinates for every unique spot on
earth.  There are only approximations based on one or other of the accepted
geoid models, however for most practical purposes good approximations are
all you need.  In Europe the official definition of WGS84 is sometime
referred to as ETRS89.  For all practical purposes in Western Europe the OS
advise that one can regard ETRS89 as identical to WGS84 (unless you need to
worry about tectonic plate movements).

## Practical implications

If you are working exclusively with British OS maps and you merely want
to convert from the grid to the latitude and longitude coordinates printed (as
faint blue crosses) on those maps, then all you need from these modules are
the plain C<grid_to_ll()> and C<ll_to_grid()> routines.  On the other hand if
you want to produce latitude and longitude coordinates suitable for Google
Earth or Wikipedia from a British grid reference, then you need an extra
step.  Convert your grid reference using C<grid_to_ll()> and then shift it
from the OSGB model to the WGS84 model using C<shift_ll_into_WGS84()>.  To
go the other way round, shift your WGS84 lat/lon coordinated into OSGB,
using C<shift_ll_from_WGS84()>, before you convert them using
C<ll_to_grid()>.

If you have a requirement for really accurate work (say to within a
millimetre or two) then you need to use the OS's transformation matrix
called OSTN02.  This monumental work published in 2002 re-defined the
British grid in terms of offsets from WGS84 to allow really accurate grid
references to be determined from really accurate GPS readings (the sort you
get from professional fixed base stations, not from your car's sat nav or
your hand-held device).  The problem with it is that it defines the grid in
terms of a deviation in three dimensions from a pseudo-grid based on WGS84
and it does this separately for every square km of the country, so the data
set is huge and takes a second or two to load even on a fast machine.
Nevertheless a Perl version of OSTN02 is included as a separate module in
this distribution just in case you really need it (but you don't need it for
any "normal" work).  Because of the way OSTN02 is defined, the sequence of
conversion and shifting works differently from the approximate routines
described above.

Starting with a really accurate lat/lon reading in WGS84 terms, you need to
transform it into a pseudo-grid reference using C<ll_to_grid()> using an
optional argument to tell it to use the WGS84 geoid parameters instead of
the default OSGB parameters.  The L<Geo::Coordinates::OSTN02> package
provides a routine called C<ETRS89_to_OSGB36()> which will shift this pseudo-grid
reference into an accurate OSGB grid reference.  To go back the other way,
you use C<OSGB36_to_ETRS89()> to make a pseudo-grid reference, and then call
C<grid_to_ll()> with the WGS84 parameter to get WGS84 lat/long coordinates.


   ($lat, $lon, $height) = (51.5, -1, 10);
   ($x, $y) = ll_to_grid($lat, $lon, 'WGS84');
   ($e, $n, $elevation) = ETRS89_to_OSGB36($x, $y, $height);

   ($x, $y, $z) = OSGB36_to_ETRS89($e, $n, $elevation);
   ($lat, $lon) = grid_to_ll($x, $y, 'WGS84');


## EXAMPLES

  # to import everything try...
  use Geo::Coordinates::OSGB ':all';

  # Get full coordinates in metres from GR
  ($e,$n) = parse_trad_grid('TQ 234 098');

  # Latitude and longitude according to the OSGB geoid (as
  # printed on OS maps), if you want them to work in Google
  # Earth or some other tool that uses WGS84 then adjust results
  ($lat, $lon) = grid_to_ll($e, $n);
  ($lat, $lon, $alt) = shift_ll_into_WGS84($lat, $lon, $alt);
  # and to go the other way
  ($lat, $lon, $alt) = shift_ll_from_WGS84($lat, $lon, $alt);
  ($e, $n) = ll_to_grid($lat,$lon);
  # In both cases the elevation is in metres (default=0m)

  # Reading and writing grid references
  # Format full easting and northing into traditional formats
  $gr1 = format_grid_trad($e, $n);    # "TQ 234 098"
  $gr1 =~ s/\s//g;                    # "TQ234098"
  $gr2 = format_grid_GPS($e, $n);      # "TQ 23451 09893"
  $gr3 = format_grid_landranger($e, $n);# "TQ 234 098 on Sheet 176"
  # or call in list context to get the individual parts
  ($sq, $e, $n) = format_grid_trad($e, $n); # ('TQ', 234, 98)

  # parse routines to convert from these formats to full e,n
  ($e,$n) = parse_trad_grid('TQ 234 098');
  ($e,$n) = parse_trad_grid('TQ234098'); # spaces optional
  ($e,$n) = parse_trad_grid('TQ',234,98); # or even as a list
  ($e,$n) = parse_GPS_grid('TQ 23451 09893'); # as above..

  # You can also get grid refs from individual maps.
  # Sheet between 1..204; gre & grn must be 3 or 5 digits long
  ($e,$n) = parse_landranger_grid(176,123,994);

  # With just the sheet number you get GR for SW corner
  ($e,$n) = parse_landranger_grid(184);

  # Reading and writing lat/lon coordinates
  ($lat, $lon) = parse_ISO_ll("+52-002/");
  $iso = format_ll_ISO($lat,$lon);  # "+520000-0020000/"
  $str = format_ll_trad($lat,$lon);   # "N52:00:00 W002:00:00"


## BUGS

The conversions are only approximate.   So after

  ($a1,$b1) = grid_to_ll(ll_to_grid($a,$b));

neither C<$a==$a1> nor C<$b==$b1>. However C<abs($a-$a1)> and C<abs($b-$b1)>
should be less than C<0.00001> which will give you accuracy to within a
metre. In the middle of the grid 0.00001 degrees is approximately 1 metre.
Note that the error increases the further away you are from the
central meridian of the grid system.

The C<format_grid_landranger()> does not take account of inset areas on the
sheets.  So if you feed it a reference for the Scilly Isles, it will tell you
that the reference is not on any Landranger sheet, whereas in fact the
Scilly Isles are on an inset in the SW corner of Sheet 203.  There is
nothing in the design that prevents me adding the insets, they just need to
be added as extra sheets with names like "Sheet 2003 Inset 1" with their own
reference points and special sheet sizes.  Collecting the data is another
matter.

Not enough testing has been done.  I am always grateful for the feedback I
get from users, but especially for problem reports that help me to make this
a better module.


## AUTHOR

Toby Thurston ---  6 Nov 2008

toby@cpan.org

## SEE ALSO

The UK Ordnance Survey's theory paper referenced above in L<Theory>.

See L<Geo::Coordinates::Convert> for a general approach (not based on the above
paper).

See L<Geo::Coordinates::Lambert> for a French approach.

=cut
