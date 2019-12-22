# Installation

This page describes the installation of OpenPhone on an Orange Pi Zero. It may run on other hardware as well, such as Raspberr Pi, but this has not been tested yet. Feel free to send pull requests to improve and expand this documentation. __TODO:__ Make fully embedded images using OpenWrt or MiZy or something else.

## Install Armbian

Download and install **[Armbian](https://www.armbian.com/orange-pi-zero/)** for Orange Pi Zero to a microSD card. You can use [Etcher](https://etcher.io) to write the filesystem image to a 8 GB microSD card.

Optionally make it read-only using overlayroot as described [here](https://gist.github.com/probonopd/97f6826cc5aa3c0c0950682b0bc266bc). In this case don't forget to chroot into the rw system before executing the following steps.

## Enable SPI

Need to enable overlays for SPI and audio

```
nano /boot/armbianEnv.txt
# Make sure we have:
overlays=analog-codec i2c0 spi-spidev uart1 uart2 usbhost2 usbhost3
param_spidev_spi_bus=1
param_spidev_max_freq=100000000
```

## Install dependencies

__NOTE:__ This section may not be complete. Feel free to send pull requests to improve and expand this documentation.

Log into the machine as root. Armbian will ask you to set a new password which you need to use from thereon to log in. Once logged into the machine as root, do:

```
apt update
apt -y install git libttspico-utils python-dev python-lxml python-requests python-flask python-pyaudio mpd python-mpd python-configparser python-pip python-setuptools libhidapi-libusb0
sudo pip install wheel
sudo pip install flask-bootstrap
sudo pip install hid
```

## Install OpenPhone

First, install OpenPhone and its dependencies:

```
cd /root
git clone https://github.com/probonopd/OpenPhone
cd OpenPhone
# Get _pjsua.so and pjsua.py from https://github.com/probonopd/pjsua-static/releases and put into this directory
wget https://raw.githubusercontent.com/joosteto/ws2812-spi/master/ws2812.py
```

Then, install the SPI stuff for Neopixels:
```
git clone https://github.com/doceme/py-spidev.git
cd py-spidev
make -j4
make install
cd ..
git clone https://github.com/joosteto/ws2812-spi.git
find ws2812-spi/ -type f -name '*.py' -exec sed -i -e 's|spi.open(0,0)|spi.open(1,0)|g' {} \;
find ws2812-spi/ -type f -name '*.py' -exec sed -i -e 's|tx=\[\]|tx=\[0x00\]|g' {} \;
```

Details are on https://gist.github.com/probonopd/97f6826cc5aa3c0c0950682b0bc266bc#ws2812b-neopixels-driven-by-python.

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
