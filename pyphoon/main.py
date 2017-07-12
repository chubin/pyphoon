"""
Copyright (c) 2017 Riptide IO, Inc. All Rights Reserved.

"""
from __future__ import absolute_import, unicode_literals
import sys
import os
import locale

from math import cos, sqrt

sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "lib"))
from pyphoon.lib.astro import unix_to_julian, phase, phasehunt2
from pyphoon.lib.moons import background6, background18, background19, \
    background21, background22, background23, background24, background29, \
    background32
from pyphoon.lib.translations import LITS


def fatal(message):
    print >> sys.stderr, message
    sys.exit(1)


#
# Global defines and declarations.
#
SECSPERMINUTE = 60
SECSPERHOUR = (60 * SECSPERMINUTE)
SECSPERDAY = (24 * SECSPERHOUR)

PI = 3.1415926535897932384626433

QUARTERLITLEN = 16
QUARTERLITLENPLUSONE = 17

# If you change the aspect ratio, the canned backgrounds won't work.
ASPECTRATIO = 0.5


def putseconds(secs):
    days = secs / SECSPERDAY
    secs = secs - days * SECSPERDAY
    hours = secs / SECSPERHOUR
    secs = secs - hours * SECSPERHOUR
    minutes = secs / SECSPERMINUTE
    secs = secs - minutes * SECSPERMINUTE

    return "%ld %2ld:%02ld:%02ld" % (days, hours, minutes, secs)


def putmoon(t, numlines, atfiller, notext, lang=None):
    output = [""]

    def putchar(c):
        output[0] += c

    def fputs(s):
        output[0] += s

    if not lang:
        try:
            lang = locale.getdefaultlocale()[0]
        except:
            lang = 'en'

    # if not lang:
    #     lang = 'en'
    if '_' in lang:
        lang = lang.split('_', 1)[0]

    lits = LITS.get(lang, LITS.get('en'))
    qlits = [x + " +" for x in lits]
    nqlits = [x + " -" for x in lits]

    # Find the length of the atfiller string
    atflrlen = len(atfiller)

    # Figure out the phase
    jd = unix_to_julian(t)
    pctphase, cphase, aom, cdist, cangdia, csund, csuang = phase(jd)
    angphase = pctphase * 2.0 * PI
    mcap = -cos(angphase)

    # Figure out how big the moon is
    yrad = numlines / 2.0
    xrad = yrad / ASPECTRATIO
    numcols = xrad * 2

    # Figure out some other random stuff
    midlin = numlines / 2
    phases, which = phasehunt2(jd)

    # Now output the moon, a slice at a time
    atflridx = 0
    lin = 0
    while lin < numlines:
        # Compute the edges of this slice
        y = lin + 0.5 - yrad
        xright = xrad * sqrt(1.0 - (y * y) / (yrad * yrad))
        xleft = -xright
        if (angphase >= 0.0 and angphase < PI):
            xleft = mcap * xleft
        else:
            xright = mcap * xright

        colleft = int(xrad + 0.5) + int(xleft + 0.5)
        colright = int(xrad + 0.5) + int(xright + 0.5)

        # Now output the slice
        col = 0
        while col < colleft:
            putchar(' ')
            col += 1
        while col <= colright:
            if 6 == numlines:
                c = background6[lin][col]
            elif 18 == numlines:
                c = background18[lin][col]
            elif 19 == numlines:
                c = background19[lin][col]
            elif 21 == numlines:
                c = background21[lin][col]
            elif 22 == numlines:
                c = background22[lin][col]
            elif 23 == numlines:
                c = background23[lin][col]
            elif 24 == numlines:
                c = background24[lin][col]
            elif 29 == numlines:
                c = background29[lin][col]
            elif 32 == numlines:
                c = background32[lin][col]
            else:
                c = '@'
            if c != '@':
                putchar(c)
            else:
                putchar(atfiller[atflridx])
                atflridx = (atflridx + 1) % atflrlen
            col += 1

        if (numlines <= 27 and not notext):
            # Output the end-of-line information, if any
            fputs("\t ")
            if lin == midlin - 2:
                fputs(qlits[int(which[0] * 4.0 + 0.001)])
            elif lin == midlin - 1:
                fputs(putseconds(int((jd - phases[0]) * SECSPERDAY)))
            elif lin == midlin:
                fputs(nqlits[int(which[1] * 4.0 + 0.001)])
            elif lin == midlin + 1:
                fputs(putseconds(int((phases[1] - jd) * SECSPERDAY)))

        putchar('\n')
        lin += 1

    return output[0]