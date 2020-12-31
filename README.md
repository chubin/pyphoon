[![pyphoon](https://snapcraft.io/pyphoon/badge.svg)](https://snapcraft.io/pyphoon)


# pyphoon
ASCII Art Phase of the Moon (Python version)

![Screenshots](http://igor.chub.in/pyphoon/screenshot.png)

Based on the original version of Jef Poskanzer <jef@mail.acme.com> (Twitter: @jef_poskanzer) 
written in Pascal in 1979 (and later translated by himself into C, and now by me into Python).

# Installation via snap

~~~
$ sudo snap install pyphoon --edge

~~~

# Usage

~~~~
$ pyphoon --help
usage: pyphoon [-h] [-n LINES] [-x] [-l [LANGUAGE]]
               [-s {north,south} | -S {north,south}]
               [date]

Show Phase of the Moon

positional arguments:
  date                  Date for that the phase of the Moon must be shown.
                        Today by default

optional arguments:
  -h, --help            show this help message and exit
  -n LINES, --lines LINES
                        Number of lines to display (size of the moon)
  -x, --notext          Print no additional information, just the moon
  -l [LANGUAGE], --language [LANGUAGE]
                        locale for that the phase of the Moon must be shown.
                        English by default
  -s {north,south}, --hemisphere {north,south}
                        Earth hemisphere from which to observe the Moon. North 
						by default
  -S {north,south}, --hemispherewarning {north,south}
                        The same as -s and --hemisphere, but shows an
                        hemisphere reminder under the phase text.
~~~~

By default the number of lines is 30 and the date is today.

Pyphoon only displays the [near side](https://en.wikipedia.org/wiki/Near_side_of_the_Moon) of the Moon
because the [far side](https://en.wikipedia.org/wiki/Far_side_of_the_Moon) is never visible from Earth.
This said, the near side either shows North pole up
(for people living in northern Earth hemisphere)
or South pole up
(for people living in southern Earth hemisphere).
This in turn changes the direction of the observable crescent:
*e.g.* 🌒 or 🌘 for the first quarter.
To accomodate this, pyphoon draws the moon as seen from either hemisphere on request,
defaulting to `-s north`ern hemisphere.
If you happen to live in equatorial zones,
then the Moon shows either pole up
depending on [how you rotate your feet](https://www.unicode.org/L2/L2017/17304-moon-var.pdf),
so you only need to pick the one you like most. 

Supported dateformats:

* 2016-Mar-01
* 2016-03-01
* 03-01-2016
* 03/01/2016
* etc.

Displayed information:

* time after the previous state (-)
* time to the next state (+)
* Hemisphere from which the moon is observed (with `-S` switch on).

# Own changes

There are several changes in PyPhoon that were not present in the original Jef Pokazner's version of 1979:

* Localization: pyphoon is translated into many languages; language is configured using the system locale (`$LANG`)
* Hemisphere: pyphoon can show the moon as seen from the north or south hemisphere (south hemisphere is upside-down, waxes and wanes in the opposite direction).

# Dependencies

* dateutil

# Installation

**Latest version:**

`pip install git+https://github.com/chubin/pyphoon.git`. 

Append `--upgrade` if you have an older version.


**Longer way:**

Assuming that **git**, **python** and **pip** are already installed,
install pyphoon with the following commands in your O.S. terminal (bash, command prompt, powershell, etc):

```
git clone https://github.com/chubin/pyphoon
cd pyphoon
pip install -r requirements.txt
python setup.py install
```



after that you can simply call `pyphoon` from your terminal.

If you don't have git installed to use `git clone`, it's possible to [download](https://github.com/chubin/pyphoon/archive/master.zip) this repository and unzip it instead.

Depending on your O.S. it may be needed to prepend `sudo` to `python setup.py install`, 
or even change `python` to `python3` and `pip` to `pip3`. 
