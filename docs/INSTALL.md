# Installation

This page describes the installation of OpenPhone on an Orange Pi Zero. It may run on other hardware as well, such as Raspberr Pi, but this has not been tested yet. Feel free to send pull requests to improve and expand this documentation. __TODO:__ Nake fully embedded images using OpenWrt or MiZy or something else.

## Install Armbian

Download and install **[Armbian](https://www.armbian.com/orange-pi-zero/)** for Orange Pi Zero to a microSD card. You can use [Etcher](https://etcher.io) to write the filesystem image to a 8 GB microSD card.

## Install dependencies

__NOTE:__ This section may not be complete. Feel free to send pull requests to improve and expand this documentation.

Log into the machine as root. Armbian will ask you to set a new password which you need to use from thereon to log in. Once logged into the machine as root, do:

```
apt update
apt -y install git libttspico-utils python-lxml python-requests python-flask python-pyaudio mpd python-mpd python-configparser python-pip python-setuptools
sudo pip install wheel
sudo pip install flask-bootstrap
```

## Install OpenPhone

First, install OpenPhone and its dependencies:

```
cd /root
git clone https://github.com/probonopd/OpenPhone
cd OpenPhone
# Get _pjsua.so and pjsua.py from https://github.com/probonopd/pjsua-static/releases and put into this directory
```

Now edit `/etc/rc.local` and insert the following lines so that OpenPhone gets started automatically upon each boot:

```
# Disable ipv6 if you don't want to use it
echo 1 > /proc/sys/net/ipv6/conf/all/disable_ipv6

# Enable WLAN if you want to use it (need to configure it first)
ifconfig wlan0 up
sleep 2 ### FIXME

# Start the phone
/root/OpenPhone/openphone.py &

# File needs to end with this line (this was already there)
exit 0
```

## Connect CX300

Connect the Polycom CX300 device to the USB port

## Configure

Add a file `/root/OpenPhone/openphone.cfg` and insert:

```
[sip0]
server=sip.yourprovider.com
user=...
password=...

[fritzbox0]
host=fritz.box
```

Of course you need to use the values obtained from your SIP telephony provider for `server`, `user`, and `password`.

Additional keys may be required in the future.

## Test run

Run `/etc/rc.local`. OpenPhone should start.
