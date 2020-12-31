"""

Adapted from "moontool.c" by John Walker, Release 2.5

Quoting from the original:

  The algorithms used in this program to calculate the positions Sun and
  Moon as seen from the Earth are given in the book "Practical Astronomy
  With  Your  Calculator"  by  Peter  Duffett-Smith,   Second   Edition,
  Cambridge University Press, 1981.  Ignore the word "Calculator" in the
  title;  this  is  an  essential  reference  if  you're  interested  in
  developing  software  which  calculates  planetary  positions, orbits,
  eclipses, and  the  like.   If  you're  interested  in  pursuing  such
  programming, you should also obtain:

    "Astronomical  Formulae for Calculators" by Jean Meeus, Third Edition,
    Willmann-Bell, 1985.  A must-have.

    "Planetary  Programs  and  Tables  from  -4000  to  +2800"  by  Pierre
    Bretagnon  and Jean-Louis Simon, Willmann-Bell, 1986.  If you want the
    utmost  (outside  of  JPL)  accuracy  for  the  planets,  it's   here.

    "Celestial BASIC" by Eric Burgess, Revised Edition, Sybex, 1985.  Very
    cookbook oriented, and many of the algorithms are hard to dig  out  of
    the turgid BASIC code, but you'll probably want it anyway.

See http://www.fourmilab.ch/moontool/

Ported to Python by Igor Chubin, 2016
"""


from __future__ import print_function

import sys
from math import floor, sin, cos, sqrt, tan, atan, atan2

#  Astronomical constants

EPOCH = 2444238.5      # 1980 January 0.0

#  Constants defining the Sun's apparent orbit

ELONGE = 278.833540     # Ecliptic longitude of the Sun at EPOCH 1980.0
ELONGP = 282.596403     # Ecliptic longitude of the Sun at perigee
ECCENT = 0.016718       # Eccentricity of Earth's orbit
SUNSMAX = 1.495985e8    # Semi-major axis of Earth's orbit, km
SUNANGSIZ = 0.533128    # Sun's angular size, degrees, at semi-major axis distance

#  Elements of the Moon's orbit, EPOCH 1980.0

MMLONG = 64.975464      # Moon's mean lonigitude at the EPOCH
MMLONGP = 349.383063    # Mean longitude of the perigee at the EPOCH
MLNODE = 151.950429     # Mean longitude of the node at the EPOCH
MINC = 5.145396         # Inclination of the Moon's orbit
MECC = 0.054900         # Eccentricity of the Moon's orbit
MANGSIZ = 0.5181        # Moon's angular size at distance a from Earth
MSMAX = 384401.0        # Semi-major axis of Moon's orbit in km
MPARALLAX = 0.9507      # Parallax at distance a from Earth
SYNMONTH = 29.53058868  # Synodic month (new Moon to new Moon)
LUNATBASE = 2423436.0   # Base date for E. W. Brown's numbered series of lunations (1923 January 16)

#  Properties of the Earth

EARTHRAD = 6378.16      # Radius of Earth in kilometres


PI = 3.14159265358979323846  # Assume not near black hole nor in Tennessee

#  Handy mathematical functions

def sgn(num):
    """ Get signedness of num
    """
    return -1 if num < 0 else 1 if num > 0 else 0

def fixangle(ang):
    """ Fix angle
    """
    return ang - 360.0 * (floor((ang) / 360.0))

def torad(deg):
    """ Convert degrees to radians
    """
    return deg * PI / 180.0

def todeg(rad):
    """ Convert radians to degress
    """
    return rad * 180.0 / PI
def dsin(deg):
    """ Get sin(degrees)
    """
    return sin(torad((deg)))
def dcos(deg):
    """ Get cos(degrees)
    """
    return cos(torad((deg)))


def fatal(error):
    """ Print error and exit 1
    """
    print(error, file=sys.stderr)
    sys.exit(1)


def unix_to_julian(timestamp):
    """ UNIX_TO_JULIAN  --  Convert internal Unix date/time to astronomical
        Julian time (i.e. Julian date plus day fraction, expressed as
        a double).
    """
    return 1.0 * timestamp / 86400.0 + 2440587.4999996666666666666


def jyear(epoch):
    """ JYEAR  --  Convert Julian date to year, month, day, which are
         returned via integer pointers to integers.
        Return (yy, mm, dd)
    """

    epoch += 0.5  # Astronomical to civil
    jul = floor(epoch)
    jul -= 1721119.0
    year = floor(((4 * jul) - 1) / 146097.0)
    jul = (jul * 4.0) - (1.0 + (146097.0 * year))
    day = floor(jul / 4.0)
    jul = floor(((4.0 * day) + 3.0) / 1461.0)
    day = ((4.0 * day) + 3.0) - (1461.0 * jul)
    day = floor((day + 4.0) / 4.0)
    month = floor(((5.0 * day) - 3) / 153.0)
    day = (5.0 * day) - (3.0 + (153.0 * month))
    day = floor((day + 5.0) / 5.0)
    year = (100.0 * year) + jul
    if month < 10.0:
        month += 3
    else:
        month -= 9
        year += 1
    return (year, month, day)

def meanphase(sdate, k):
    """ MEANPHASE  --  Calculates time of the mean new Moon for a given
          base date.  This argument K to this function is
          the precomputed synodic month index, given by:

              K = (year - 1900) * 12.3685

          where year is expressed as a year and fractional year.

    """
    # Time in Julian centuries from 1900 January 0.5
    jul_time = (sdate - 2415020.0) / 36525
    jul_time2 = jul_time * jul_time   # Square for frequent use
    jul_time3 = jul_time2 * jul_time  # Cube for frequent use

    return (
        2415020.75933 + SYNMONTH * k
        + 0.0001178 * jul_time2
        - 0.000000155 * jul_time3
        + 0.00033 * dsin(166.56 + 132.87 * jul_time - 0.009173 * jul_time2)
    )

def truephase(k, moonphase):
    """ TRUEPHASE  --  Given a K value used to determine the
          mean phase of the new moon, and a phase
          selector (0.0, 0.25, 0.5, 0.75), obtain
          the true, corrected phase time.
  """

    apcor = False

    k += moonphase                    # Add phase to new moon time
    jul_time = k / 1236.85            # Time in Julian centuries from 1900 January 0.5
    jul_time2 = jul_time * jul_time   # Square for frequent use
    jul_time3 = jul_time2 * jul_time  # Cube for frequent use

    # Mean time of phase
    phasetime = (
        2415020.75933
        + SYNMONTH * k
        + 0.0001178 * jul_time2
        - 0.000000155 * jul_time3
        + 0.00033 * dsin(166.56 + 132.87 * jul_time - 0.009173 * jul_time2)
    )

    # Sun's mean anomaly
    sun_mean_anom = (
        359.2242
        + 29.10535608 * k
        - 0.0000333 * jul_time2
        - 0.00000347 * jul_time3
    )

    # Moon's mean anomaly
    moon_mean_anom = (
        306.0253
        + 385.81691806 * k
        + 0.0107306 * jul_time2
        + 0.00001236 * jul_time3
    )

    # Moon's argument of latitude
    moon_arg_lat = (
        21.2964
        + 390.67050646 * k
        - 0.0016528 * jul_time2
        - 0.00000239 * jul_time3
    )

    if (moonphase < 0.01) or (abs(moonphase - 0.5) < 0.01):
        # Corrections for New and Full Moon
        phasetime += (
            (0.1734 - 0.000393 * jul_time) * dsin(sun_mean_anom)
            + 0.0021 * dsin(2 * sun_mean_anom)
            - 0.4068 * dsin(moon_mean_anom)
            + 0.0161 * dsin(2 * moon_mean_anom)
            - 0.0004 * dsin(3 * moon_mean_anom)
            + 0.0104 * dsin(2 * moon_arg_lat)
            - 0.0051 * dsin(sun_mean_anom + moon_mean_anom)
            - 0.0074 * dsin(sun_mean_anom - moon_mean_anom)
            + 0.0004 * dsin(2 * moon_arg_lat + sun_mean_anom)
            - 0.0004 * dsin(2 * moon_arg_lat - sun_mean_anom)
            - 0.0006 * dsin(2 * moon_arg_lat + moon_mean_anom)
            + 0.0010 * dsin(2 * moon_arg_lat - moon_mean_anom)
            + 0.0005 * dsin(sun_mean_anom + 2 * moon_mean_anom)
        )
        apcor = True
    elif (abs(moonphase - 0.25) < 0.01 or (abs(moonphase - 0.75) < 0.01)):
        phasetime += (
            (0.1721 - 0.0004 * jul_time) * dsin(sun_mean_anom)
            + 0.0021 * dsin(2 * sun_mean_anom)
            - 0.6280 * dsin(moon_mean_anom)
            + 0.0089 * dsin(2 * moon_mean_anom)
            - 0.0004 * dsin(3 * moon_mean_anom)
            + 0.0079 * dsin(2 * moon_arg_lat)
            - 0.0119 * dsin(sun_mean_anom + moon_mean_anom)
            - 0.0047 * dsin(sun_mean_anom - moon_mean_anom)
            + 0.0003 * dsin(2 * moon_arg_lat + sun_mean_anom)
            - 0.0004 * dsin(2 * moon_arg_lat - sun_mean_anom)
            - 0.0006 * dsin(2 * moon_arg_lat + moon_mean_anom)
            + 0.0021 * dsin(2 * moon_arg_lat - moon_mean_anom)
            + 0.0003 * dsin(sun_mean_anom + 2 * moon_mean_anom)
            + 0.0004 * dsin(sun_mean_anom - 2 * moon_mean_anom)
            - 0.0003 * dsin(2 * sun_mean_anom + moon_mean_anom)
        )
        if moonphase < 0.5:
            # First quarter correction
            phasetime += 0.0028 - 0.0004 * dcos(sun_mean_anom) + 0.0003 * dcos(moon_mean_anom)
        else:
            # Last quarter correction
            phasetime += -0.0028 + 0.0004 * dcos(sun_mean_anom) - 0.0003 * dcos(moon_mean_anom)
        apcor = True
    if not apcor:
        fatal("TRUEPHASE called with invalid phase selector")
    return phasetime


def phasehunt5(sdate):
    """ PHASEHUNT5  --  Find time of phases of the moon which surround
         the current date.  Five phases are found, starting
         and ending with the new moons which bound the
         current lunation.
        Return phases (double[5])
    """

    adate = sdate - 45

    year, month, _ = jyear(adate)
    var1 = floor((year + ((month - 1) * (1.0 / 12.0)) - 1900) * 12.3685)

    new_time = meanphase(adate, var1)
    adate = new_time
    while True:
        adate += SYNMONTH
        var2 = var1 + 1
        newer_time = meanphase(adate, var2)
        if newer_time > sdate >= new_time:
            break
        new_time = newer_time
        var1 = var2
    return [truephase(var1, x) for x in [0.0, 0.25, 0.5, 0.75]] + [truephase(var2, 0.0)]


def phasehunt2(sdate):
    """ PHASEHUNT2  --  Find time of phases of the moon which surround
         the current date.  Two phases are found.
        Return phases[2], which[2]
    """
    phases = [0, 0]
    which = [0, 0]

    phases5 = phasehunt5(sdate)
    phases[0] = phases5[0]
    which[0] = 0.0
    phases[1] = phases5[1]
    which[1] = 0.25
    if phases[1] <= sdate:
        phases[0] = phases[1]
        which[0] = which[1]
        phases[1] = phases5[2]
        which[1] = 0.5
        if phases[1] <= sdate:
            phases[0] = phases[1]
            which[0] = which[1]
            phases[1] = phases5[3]
            which[1] = 0.75
            if phases[1] <= sdate:
                phases[0] = phases[1]
                which[0] = which[1]
                phases[1] = phases5[4]
                which[1] = 0.0

    return phases, which


def kepler(angle, ecc):
    """ KEPLER  --   Solve the equation of Kepler.
    """

    epsilon = 1E-6
    angle = torad(angle)
    theta = angle

    while True:
        delta = theta - ecc * sin(theta) - angle
        theta -= delta / (1 - ecc * cos(theta))
        if abs(delta) <= epsilon:
            break

    return theta


def phase(pdate):  # pylint: disable=too-many-locals
    """ PHASE  --  Calculate phase of moon as a fraction:

         The argument is the time for which the phase is requested,
         expressed as a Julian date and fraction.  Returns the terminator
         phase angle as a percentage of a full circle (i.e., 0 to 1),
         and stores into pointer arguments the illuminated fraction of
             the Moon's disc, the Moon's age in days and fraction, the
         distance of the Moon from the centre of the Earth, and the
         angular diameter subtended by the Moon as seen by an observer
         at the centre of the Earth.

        pphase:      Illuminated fraction
        mage:        Age of moon in days
        dist:        Distance in kilometres
        angdia:      Angular diameter in degrees
        sudist:      Distance to Sun
        suangdia:    Sun's angular diameter

        Returns (phase, moon_phase, mage, dist, angdia, sudist, suangdia)
    """

    # Calculation of the Sun's position

    day = pdate - EPOCH  # Date within EPOCH
    sun_mean_anom = fixangle((360 / 365.2422) * day)  # Mean anomaly of the Sun
    epoch_1980 = fixangle(sun_mean_anom + ELONGE - ELONGP)  # Convert from perigee
                                                   # co-ordinates to EPOCH 1980.0
    ecc = kepler(epoch_1980, ECCENT)  # Solve equation of Kepler
    ecc = sqrt((1 + ECCENT) / (1 - ECCENT)) * tan(ecc / 2)
    ecc = 2 * todeg(atan(ecc))  # True anomaly
    lambdasun = fixangle(ecc + ELONGP)  # Sun's geocentric ecliptic longitude

    orbital_dist = ((1 + ECCENT * cos(torad(ecc))) / (1 - ECCENT * ECCENT))  # Orbital distance factor
    sun_dist = SUNSMAX / orbital_dist                   # Distance to Sun in km
    sun_ang = orbital_dist * SUNANGSIZ                  # Sun's angular size in degrees

    # Calculation of the Moon's position

    moon_mean_long = fixangle(13.1763966 * day + MMLONG)  # Moon's mean longitude

    moon_mean_anom = fixangle(moon_mean_long - 0.1114041 * day - MMLONGP)  # Moon's mean anomaly

    moon_asc_node_mean_long = fixangle(MLNODE - 0.0529539 * day)  # Moon's ascending node mean longitude

    evection = 1.2739 * sin(torad(2 * (moon_mean_long - lambdasun) - moon_mean_anom))  # Evection

    ann_eq = 0.1858 * sin(torad(epoch_1980))  # Annual equation

    correction1 = 0.37 * sin(torad(epoch_1980))  # Correction term

    moon_anom_correct = moon_mean_anom + evection - ann_eq - correction1  # Corrected anomaly

    centre_eq_correct = 6.2886 * sin(torad(moon_anom_correct))  # Correction for the equation of the centre

    # Another correction term
    correction2 = 0.214 * sin(torad(2 * moon_anom_correct))

    long_correct = moon_mean_long + evection + centre_eq_correct - ann_eq + correction2  # Corrected longitude

    variation = 0.6583 * sin(torad(2 * (long_correct - lambdasun)))  # Variation

    true_long = long_correct + variation  # True longitude

    node_long_correct = moon_asc_node_mean_long - 0.16 * sin(torad(epoch_1980))  # Corrected longitude of the node

    y_incline = sin(torad(true_long - node_long_correct)) * cos(torad(MINC))  # Y inclination coordinate

    x_incline = cos(torad(true_long - node_long_correct))  # X inclination coordinate

    lambdamoon = todeg(atan2(y_incline, x_incline))  # Ecliptic longitude
    lambdamoon += node_long_correct

    # Calculation of the phase of the Moon

    moon_age = true_long - lambdasun  # Age of the Moon in degrees

    moon_dist = (  # Calculate distance of moon from the centre of the Earth
        (MSMAX * (1 - MECC * MECC))
        / (1 + MECC * cos(torad(moon_anom_correct + centre_eq_correct)))
    )

    moon_diam_frac = moon_dist / MSMAX  # Calculate Moon's angular diameter
    moon_ang = MANGSIZ / moon_diam_frac

    moon_phase = (1 - cos(torad(moon_age))) / 2  # Phase of the Moon
    mage = SYNMONTH * (fixangle(moon_age) / 360.0)
    dist = moon_dist
    angdia = moon_ang
    sudist = sun_dist
    suangdia = sun_ang

    return (
        fixangle(moon_age) / 360.0,
        moon_phase,
        mage,
        dist,
        angdia,
        sudist,
        suangdia
    )
