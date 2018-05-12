#!/usr/bin/env python

import mpd # sudo apt -y install mpd python-mpd
import time

class MpdPlayer(object):

    def __init__(self):

        self.mpd_client = mpd.MPDClient(use_unicode=True)
        self.mpd_client.connect("localhost", 6600)
        print(self.mpd_client.mpd_version) 
        print(self.mpd_client.status())
        print(self.mpd_client.outputs())

        for entry in self.mpd_client.lsinfo("/"):
            print("%s" % entry)
        for key, value in self.mpd_client.status().items():
            print("%s: %s" % (key, value))

        self.mpd_client.clear() # Clear current playlist
        url = "http://swr-swr1-bw.cast.addradio.de/swr/swr1/bw/mp3/128/stream.mp3"
        self.mpd_client.add(url) # Add one URL
        self.mpd_client.single(1) # Stop playing after one go (do not repeat)
        self.mpd_client.consume(1) # Remove played songs from playlist
        try:
            self.mpd_client.setvol(80) # 0-100
        except:
            print("Cannot set volume.")
            print("Some issue with the sound setup, may need to edit /etc/mpd.conf like this:")
            print("""audio_output {
                type            "alsa"
                name            "CX300"
                device          "hw:CX300" # As determined by aplay -l: "card 1: CX300 [Polycom CX300], device 0: USB Audio [USB Audio]"
                mixer_type      "software"
                mixer_device    "default"                 
        }
        samplerate_converter "internal" # Remove stutter and high CPU usage""")
            print("Try on the command line:")
            print("mpc volume 10")
            exit(1)

        for entry in self.mpd_client.lsinfo("/"):
            print("%s" % entry)
        for key, value in self.mpd_client.status().items():
            print("%s: %s" % (key, value))

    def play(self):
        time.sleep(0.2)
        print("MPD Play")
        self.mpd_client.play()

    def pause(self):
        print("MPD Pause")
        self.mpd_client.stop()
        time.sleep(0.2)


if(__name__=="__main__"):
    MPD = MpdPlayer()
    MPD.play()