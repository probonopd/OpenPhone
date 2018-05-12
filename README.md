# OpenPhone
Open source desk telephone implemented in Python and pjsua

## Rationale

This project contains the software for an extensible open source VOIP (voice-over-IP) desk telephone implemented in Python and pjsua, using inexpensive hardware such as an Orange Pi Zero. Using it, you can build

* A VOIP upgrade to existing analog desk phones
* A VOIP desk phone
* A VOIP conference phone

Commercial VOIP desk phones are often outdated, inflexible, expensive, and use proprietary hardware and software. 

This project aspires to build an extensible, customizable open source desk telephone from inexpensive components that matches (and exceeds) the user experience of an analog or ISDN desk phone.

## Features

Hardware features

* Use existing Ethernet and WLAN infrastructure (no DECT needed)
* Can be powered using a normal 5V power supply (no 48V Power-over-Ethernet needed)
* Has the physical appearance of a normal desk phone

Software features

* Use SIP accounts
* Speak the numbers while dialing to make dialing easier
* Speak the name of the caller when a call comes in; also display the name of the caller in the display. Get the name of the caller from various online and local databases
* Use the tones known from the local phone network (e.g., 1TR110 in Germany)
* …and many more, plus plenty of room to realize *your own* ideas!

## Hardware

OpenPhone is written in Python and can easily be extended to support additional hardware, such as single-board computers, sound cards, speakers, amplifiers, keyboards, cameras, network devices, etc.

The initial focus of the project is on using

* **[Orange Pi Zero](https://de.aliexpress.com/store/1553371)** single board computer (can be ordered from China for around USD 10). This runs the logic of the phone. It provides an Ethernet jack for wired networking and a WLAN interface for wireless networking. Mobile networking could be added via USB. It can be powered through a normal 5V USB power supply
* **[Polycom CX300](https://gist.github.com/probonopd/a93f65560de35ebba095f7c97a68db54)** USB desk phone (conisting of handset, speaker, keyboard, display exposed over a USB interface, but no phone logic built in). This is used as a quick-start hardware for the phone, although OpenPhone can be used with other hardware devices as well

## Software stack

The OpenPhone runs on the following software stack:

* **[Armbian](https://www.armbian.com/orange-pi-zero/)** for Orange Pi Zero (it may run on Raspbian as well). It may be desirable to move to a smaller base system such as OpenWrt or miZy to shrink its footprint (contributions welcome)
* **[python-pjsua](http://www.pjsip.org/)** SIP client library for Python. pjsua is part of th PJSIP project which is at the base of many softphones

## Installation and usage

Please refer to the [docs](docs) directory.
