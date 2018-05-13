#!/usr/bin/env python
# -*- coding: utf-8 -*-

debug = True

import os, sys, threading, time, gettext, re
from flask import Flask, jsonify, render_template, request  # apt install python-flask
import atexit
import wave # apt install python-pyaudio

import pjsua as pj

LOG_LEVEL=5
current_call = None

wav_slot = None # The slot on which ringtones etc. are played

# For Neopixels
import spidev
import ws2812

from cx300 import CX300
#from mpdplayer import MpdPlayer

from config import config
import reverse
import keyboard

reload(sys)
sys.setdefaultencoding('utf8')

t = gettext.translation('openphone', localedir=os.path.dirname(__file__)+"/locale", languages=['de'])
t.install()
_ = t.gettext

app = Flask(__name__)

cx300 = None
keyb = None

number_to_be_dialed = []
last_number_dialed = []

#mpd = MpdPlayer()
#mpd.pause()

#
# We pass this delegate to the class that handles the CX300 hardware
# so that it can call the callbacks contained herein;
# you could write a similar delegate to handle callbacks from
# another class for different hardware
# 

class DelegateForCX300:
    def on_hook(self):
        print("Delegate on_hook acting...")
        onhook()
    def off_hook(self):
        print("Delegate off_hook acting...")
        offhook()
    def on_speaker(self):
        print("Delegate on_speaker acting...")
        speaker()
    def off_speaker(self):
        print("Delegate off_speaker acting...")
    def on_headphones(self):
        print("Delegate on_headphones acting...")
    def off_headphones(self):
        print("Delegate off_headphones acting...")
    def on_mute(self):
        print("Delegate on_mute acting...")
    def off_mute(self):
        print("Delegate off_mute acting...")
    def key_down(self, key):
        key=int(key)
        print("Delegate key_down(%i) acting..." % (key))
    def key_up(self, key, time_key_was_pressed):
        key=int(key)
        print("Delegate key_up(%i, %f) acting..." % (key, time_key_was_pressed))
        if(key==10):
            key="*"
        if(key==11):
            key="#"
        if(key==12):
            redial()
        elif(key==13):
            pass # TODO: Hold
        elif(key==14):
            number_to_be_dialed.pop()
            if(cx300):
                cx300.display_two_lines("".join(number_to_be_dialed))
        else:
            handleKeypress(str(key))
    def long_press(self, key):
        print("Delegate long_press(%i) acting..." % (key))


#
# What should happen when this application quits
#

def shutdown():
    print("Shutting down")
    neopixels_off()

atexit.register(shutdown)

#
# What should happen when certain phone functionality is invoked 
#

def alarm(message):
    print("ALARM: %s" % (message))
    neopixels_red()

def redial():
    if(current_call == None):
        dial(last_number_dialed)

def stop_sounds():
    # Stop any ringing, ringback, etc. sounds
    # mpd.pause()
    global wav_slot
    print("stop_sounds running")
    try:
        pj.Lib.instance().conf_disconnect(wav_slot, 0)
    except:
        print("stop_sounds failed")
        pass

def dial(number):
    global wav_slot
    if(current_call == None):
        neopixels_off()
        if len(number) > 0:
            reversed = reverse.reverse(number).replace("Anruf von ", "").replace("Anruf aus ", "").replace("von", "").replace(" aus ", " in ")
            slow_number=' '.join(number[i:i + 1] for i in xrange(0, len(number), 1))
            if(reversed):
                print(_("Dialing %s") % (reversed))
                if(cx300):
                    cx300.display_two_lines(_("Dialing %s") % (reversed))
                speak_wait(_("Dialing %s") % (reversed))

            else:
                print(_("Dialing %s") % (number))
                if(cx300):
                    cx300.display_two_lines(_("Dialing %s") % (number))
                speak_wait(_("Dialing %s") % (str(slow_number)))
            
            neopixels_yellow()
            last_number_dialed = number_to_be_dialed
            number_to_be_dialed[:] = [] # Clear
            address = str("sip:" + str(number) + "@" + config['sip0']['server']).strip()
            make_call(address)
            # make_call("sip:thetestcall@sip.linphone.org") # Need a local account for this?
        else:
            print("No number entered yet, play dialtone or say text")
            neopixels_green()

            speak(_("Please enter a phone number"))
            if(cx300):
                cx300.display_two_lines(_("Please enter a phone number"))
                # cx300.device.write(CX300.SPEAKER_LED_OFF) # FIXME: This results in a "on hook" message! Upon which we kill the dialtone...
            stop_sounds()
            tone_file=os.path.realpath(os.path.dirname(__file__)+'/sounds/1TR110/'+config['Phone']['dial_tone'])
            wav_player_id=pj.Lib.instance().create_player(str(tone_file),loop=True)
            wav_slot=pj.Lib.instance().player_get_slot(wav_player_id)
            pj.Lib.instance().conf_connect(wav_slot, 0)

#
# What should happen when keys are pressed
#

def handleKeypress(key):
    if(current_call):
        current_call.dial_dtmf(key)
    else:
        stop_sounds()
        speak(_(key))
        number_to_be_dialed.append(key)
        if(cx300):
            cx300.display_two_lines("".join(number_to_be_dialed))

def answer_call():
    print("Answering call")
    lib.thread_register("python worker")
    current_call.answer(200) # "OK"

def offhook():
    lib.thread_register("python worker")
    if not current_call:
        dial(''.join(map(str, number_to_be_dialed)))
    else:
        print(current_call.info().state_text)
        if(current_call.info().state_text == "CONNECTING"):
            answer_call() # Only do this if "CONNECTING", else crash

def speaker():
    lib.thread_register("python worker")
    if not current_call:
        dial(''.join(map(str, number_to_be_dialed)))
    else:
        print(current_call.info().state_text)
        if(current_call.info().state_text == "CONNECTING"):
            answer_call() # Only do this if "CONNECTING", else crash

def onhook():
    global number_to_be_dialed
    print("ONHOOK!!")
    number_to_be_dialed[:] = [] # Clear
    neopixels_off()
    stop_sounds()
    if not current_call:
        print "There is no call"
    else:
        lib.thread_register("python worker")
        current_call.hangup()
    if(cx300):
        cx300.display_clear()
    #mpd.play()

#
# Neopixel functions
#

def neopixels_off():
    ws2812.write2812(spi, [[0,0,0]]*16)

def neopixels_green():
    ws2812.write2812(spi, [[5,0,0]]*16)

def neopixels_yellow():
    ws2812.write2812(spi, [[5,5,0]]*16)

def neopixels_red():
    ws2812.write2812(spi, [[0,5,0]]*16)

def neopixels_blue():
    ws2812.write2812(spi, [[0,0,5]]*16)

def neopixels_white():
    ws2812.write2812(spi, [[3,3,3]]*16)

#
# Handle key presses on CX300; can write your own similar functions for different devices
#

@app.before_first_request
def cx300_listen_keys():
    
    def run_job():
        cx300.watch_keyboard()

    thread = threading.Thread(target=run_job)
    thread.start()

#
# Handle key presses on keyboard; can write your own similar functions for different devices
#

@app.before_first_request
def keyboard_listen_keys():
    
    def run_job():
        keyb.watch_keyboard()

    thread = threading.Thread(target=run_job)
    thread.start()

#
# Web interface
#

@app.route('/_add_numbers')
def add_numbers():
    a = request.args.get('a', 0, type=int)
    b = request.args.get('b', 0, type=int)
    return jsonify(result=a + b)

@app.route('/')
def index():
    return render_template('index.html')

#
# pjsip functions
#

# Callback to receive events from account
class MyAccountCallback(pj.AccountCallback):
    sem = None

    def __init__(self, account=None):
        pj.AccountCallback.__init__(self, account)

    # Notification on incoming call
    def on_incoming_call(self, call):
        global current_call
        global wav_slot
        if current_call:
            call.answer(486, "Busy") # We answer with "busy" if this device is already in a call
            return

        # Play ringtone prior to trying to reverse
        stop_sounds()
        tone_file=os.path.realpath(os.path.dirname(__file__)+'/sounds/1TR110/'+config['Phone']['ring_tone'])
        wav_player_id=pj.Lib.instance().create_player(str(tone_file),loop=True)
        wav_slot=pj.Lib.instance().player_get_slot(wav_player_id)
        pj.Lib.instance().conf_connect(wav_slot, 0)

        print "Incoming call from ", call.info().remote_uri
        print "Press 'a' to answer"
        number = re.findall("<sip:([0-9]*?)@.*?>", call.info().remote_uri)[0]
        speakable_number = number.replace(config['Phone']['international_call_prefix'],"").replace(config['Phone']['country_code'].replace("+", ""),"")
        print(speakable_number)
        reversed=reverse.reverse(speakable_number, config['Phone']['language'])
        if(reversed != None):
            speak(reversed)
            if(cx300):
                cx300.display_two_lines(reversed)
        else:
            speak(_("Incoming call"))
            if(cx300):
                cx300.display_two_lines(_("Incoming call"))
        current_call = call

        call_cb = MyCallCallback(current_call)
        current_call.set_callback(call_cb)

        current_call.answer(180) # "Ringing"
        # current_call.answer(200) # Would answer it immediately; Working
        return

    def wait(self):
        self.sem = threading.Semaphore(0)
        self.sem.acquire()

    def on_reg_state(self):
        if self.sem:
            if self.account.info().reg_status >= 200:
                self.sem.release()


def log_cb(level, str, len):
    print str

# Text to speech
def speak(text, lang=config['Phone']['language'], loop=False):
    def run_job():
        #mpd.pause()
        lib.thread_register("python worker")
        speak_wait(text=text, lang=lang)
    thread = threading.Thread(target=run_job)
    thread.start()

def speak_wait(text, lang=config['Phone']['language']):
    ###lib.thread_register("python worker") # Would crash here!
    #mpd.pause()
    text = re.sub('(?=\d)', ' ', text) # Split numbers
    print("Vocalizing '%s'" % (text))
    os.system('pico2wave --lang="'+lang+'" -w /tmp/speech.wav "'+text+'"')
    wfile = wave.open("/tmp/speech.wav")
    ms = (1.0 * wfile.getnframes ()) / wfile.getframerate ()
    print str(ms) + "ms"
    wfile.close()
    wav_player_id=pj.Lib.instance().create_player('/tmp/speech.wav',loop=False)
    wav_slot=pj.Lib.instance().player_get_slot(wav_player_id)
    pj.Lib.instance().conf_connect(wav_slot, 0)
    time.sleep(ms)
    pj.Lib.instance().player_destroy(wav_player_id)

# Callback to receive events from Call
class MyCallCallback(pj.CallCallback):

    def __init__(self, call=None):
        pj.CallCallback.__init__(self, call)

    # Notification when call state has changed
    def on_state(self):
        global current_call
        global wav_slot
        current_call = self.call
        neopixels_white()
        print "Call with", self.call.info().remote_uri,
        print "is", self.call.info().state_text,
        print "last code =", self.call.info().last_code, 
        print "(" + self.call.info().last_reason + ")"

        if(self.call.info().role == 0): # If we are calling someone (rather than being called)
            if(self.call.info().last_code == 180):
                speak_wait(_("Ringing"))
                print("Remote phone is ringing, play local ringback tone!")
                # FIXME: Apparently the other end can signal 183 followed by 180, in which case
                # we should NOT play a local ringtone. Example: T-Mobile Germany
                stop_sounds()
                tone_file=os.path.realpath(os.path.dirname(__file__)+'/sounds/1TR110/'+config['Phone']['ringback_tone'])
                wav_player_id=pj.Lib.instance().create_player(str(tone_file),loop=True)
                wav_slot=pj.Lib.instance().player_get_slot(wav_player_id)
                pj.Lib.instance().conf_connect(wav_slot, 0)
            elif(self.call.info().last_code == 183):
                print("Remote phone is ringing, do not play local ringback tone!")
            elif(self.call.info().last_code == 486):
                print("The other side is busy!")
                speak_wait(_("Busy"))
                stop_sounds()
                tone_file=os.path.realpath(os.path.dirname(__file__)+'/sounds/1TR110/'+config['Phone']['busy_tone'])
                wav_player_id=pj.Lib.instance().create_player(str(tone_file),loop=True)
                wav_slot=pj.Lib.instance().player_get_slot(wav_player_id)
                pj.Lib.instance().conf_connect(wav_slot, 0)

        if self.call.info().state == pj.CallState.DISCONNECTED:
            current_call = None
            neopixels_off()
            stop_sounds()
            print 'Current call is', current_call
            speak(_("Disconnected"))
            if(cx300):
                cx300.device.write(CX300.SPEAKER_LED_OFF)
                # cx300.display_two_lines(str(self.call.info().last_code) + " " + self.call.info().last_reason)
                # time.sleep(10)
                cx300.display_clear()

    # Notification when call's media state has changed.
    def on_media_state(self):
        if self.call.info().media_state == pj.MediaState.ACTIVE:
            # Connect the call to sound device
            call_slot = self.call.info().conf_slot
            pj.Lib.instance().conf_connect(call_slot, 0)
            pj.Lib.instance().conf_connect(0, call_slot)
            print "Media is now active"
        else:
            print "Media is inactive"


# Function to make call
def make_call(uri):
    lib.thread_register("python worker") # Otherwise getting
    # python: ../src/pj/os_core_unix.c:692: pj_thread_this: Assertion `!"Calling pjlib from unknown/external thread.
    # You must " "register external threads with pj_thread_register() " "before calling any pjlib functions."' failed.
    # when trying to make a call!
    try:
        print "Making call to", uri
        return acc.make_call(uri, cb=MyCallCallback())
    except pj.Error, e:
        print "Exception: " + str(e)
        return None

#
# Timer class for periodic tasks 
#

class Timer(threading.Thread):
    def __init__(self, func, sec=30):
        super(Timer, self).__init__()
        self.func = func
        self.sec = sec
        self.running = True

    def stop(self):
        self.running = False

    def run(self):
        while self.running:
            t = time.time()
            self.func()
            time_elapsed = time.time()-t
            time.sleep(self.sec-time_elapsed if time_elapsed > 0 else 0)

#
# Main 
#

if __name__ == "__main__":
    spi = spidev.SpiDev() # For Neopixels
    spi.open(1,0) # For Neopixels
    lib = pj.Lib()

    # Do this check here so that we don't crash when any of the tones are missing once we want to play them
    for tone in ['dial_tone', 'ring_tone', 'ringback_tone', 'busy_tone', 'congestion_tone', 'call_waiting_tone']:
        if not (os.path.isfile(os.path.dirname(__file__)+'/sounds/1TR110/'+config['Phone'][tone])):
            print("ring_tone missing, exiting")
            exit(1)

    try:
        lib.init(log_cfg = pj.LogConfig(level=3, callback=log_cb))

        # List all sound devices and select one we want
        snd_devs = lib.enum_snd_dev()
        i = 0
        for snd_dev in snd_devs:
            print("%i: %s" % (i, snd_dev.name))
            if(snd_dev.name.startswith("plughw:CARD=CX300")):
                lib.set_snd_dev(i, i)
            i = i+1

        lib.create_transport(pj.TransportType.UDP, pj.TransportConfig(5080))
        lib.start()

        if "sip0" in config.sections():
            acc = lib.create_account(pj.AccountConfig(str(config['sip0']['server']), str(config['sip0']['user']), str(config['sip0']['password'])))
        else:
            pass
            # acc = lib.create_account_for_transport(transport, cb=MyAccountCallback())

        # Create UDP transport which listens to any available port
        transport = lib.create_transport(pj.TransportType.UDP, pj.TransportConfig(0))
        print "\nListening on", transport.info().host, 
        print "port", transport.info().port, "\n"

        my_sip_uri = "sip:" + transport.info().host + ":" + str(transport.info().port)
        print "My SIP URI is", my_sip_uri

        acc_cb = MyAccountCallback(acc)
        acc.set_callback(acc_cb)
        ###acc_cb.wait()
        print "\n"
        print "Registration complete, status=", acc.info().reg_status, \
              "(" + acc.info().reg_reason + ")"

        neopixels_green()
        time.sleep(1)
        neopixels_off()
    except pj.Error, e:
        print "Exception: " + str(e)
        lib.destroy()
        neopixels_red()

    d = DelegateForCX300()
    keyb = keyboard.Keyboard(d)

    try:
        cx300 = CX300(d)
    except:
        print("Could not open CX300, will not be able to respond to CX300 commands")
 
    if(cx300):
        # cx300.display_clear()
        cx300.display_two_lines(_("Started"))
        cx300_listen_keys()

    speak(_("Started"))

    app.run(host='0.0.0.0', port=80)

