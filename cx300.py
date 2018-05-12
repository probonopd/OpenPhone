#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hid, time, threading

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

class CX300:
    """Polycom CX300 USB phone"""

    STATUS_AVAILABLE = [0x16, 0x01]
    STATUS_BUSY = [0x16, 0x03]
    STATUS_BE_RIGHT_BACK = [0x16, 0x05]
    STATUS_AWAY = [0x16, 0x05]
    STATUS_DO_NOT_DISTURB = [0x16, 0x06]
    STATUS_OFF_WORK = [0x16, 0x07]

    STATUS_LED_GREEN = [0x16, 0x01]
    STATUS_LED_RED = [0x16, 0x03]
    STATUS_LED_ORANGE_RED = [0x16, 0x04]
    STATUS_LED_ORANGE = [0x16, 0x05]
    STATUS_LED_OFF = [0x16, 0x07]
    STATUS_LED_GREEN_ORANGE = [0x16, 0x08]

    SPEAKER_LED_OFF = [0x02, 0x00]
    SPEAKER_LED_ON = [0x02, 0x01]

    DISPLAY_CLEAR = [0x13, 0x00]

    TEXT_FOUR_CORNERS = [0x13, 0x0D]
    TEXT_TOP_LEFT = [0x14, 0x01, 0x80]
    TEXT_BOTTOM_LEFT = [0x14, 0x02, 0x80]
    TEXT_TOP_RIGHT = [0x14, 0x03, 0x80]
    TEXT_BOTTOM_RIGHT = [0x14, 0x04, 0x80]

    TEXT_TWO_LINES = [0x13, 0x15]
    TEXT_TOP_LINE = [0x14, 0x05, 0x80]
    TEXT_BOTTOM_LINE = [0x14, 0x0A, 0x80]

    def __init__(self, delegate=None):
        self.last_command = [0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00]
        self.time_last_key_down = None
        if(delegate):
            self.delegate = delegate
        self.speaker_on = False
        try:
            self.device = hid.device()
            self.device.open(0x095d, 0x9201)
            print("Manufacturer: %s" % self.device.get_manufacturer_string())
            print("Product: %s" % self.device.get_product_string())
            print("Serial No: %s" % self.device.get_serial_number_string())
        except IOError as ex:
            print(ex)

        self.device.set_nonblocking(1)

        self.keepalive()

        self.device.write(CX300.SPEAKER_LED_OFF)

        self.timer = Timer(self.keepalive) # Need to periodically send the feature report
        self.timer.start()

        # print(dir(self.device))

    def keepalive(self):
        # Send feature report - without this the phone asks to upgrade Office Communicator
        self.device.send_feature_report([0x17, 0x09, 0x04, 0x01, 0x02])

    def close(self):
        print("Closing the device")
        self.device.close()

    def display_clear(self):
        self.device.write(CX300.DISPLAY_CLEAR)

    def display_two_lines(self, first_line, second_line=""):
        first_line = str(first_line).decode('utf-8') # Umlauts work this way
        second_line = str(second_line).decode('utf-8')  # Umlauts work this way
        self.display_clear() # Needed, otherwise doesn't clear the screen in case of empty string
        self.device.write(CX300.TEXT_TWO_LINES)

        # text = text.ljust(16) # make it 16 characters long
        # If the text in the first line is too long, then print the rest in the
        # second line. TODO: Could split this on whitespace/word boundaries
        if((len(first_line)>24) and (second_line=="")):
            print("Putting text in second line")
            second_line=first_line[23:48]
            first_line=first_line[0:23]

        l=1
        for text in [first_line, second_line]:

            if(l==1):
                self.device.write(CX300.TEXT_TOP_LINE)
            elif(l==2):
                self.device.write(CX300.TEXT_BOTTOM_LINE)
            filler = [0x00] * 8
            longchunk = []

            chunks = [text[i:i + 8] for i in range(0, len(text), 8)]
            print(chunks)

            i = 0
            for chunk in chunks:
                hexchunk = [ord(x) for x in chunk]
                for j in range(8 - len(hexchunk)):
                    hexchunk.append(0x00)

                longchunk = [item for sublist in zip(hexchunk, filler) for item in sublist]
                longchunk.insert(0, 0x15)
                if (i < len(chunks)-1):
                    longchunk.insert(1, 0x00)
                else:
                    longchunk.insert(1, 0x80)
                # print [hex(no) for no in longchunk]
                self.device.write(longchunk)
                i = i + 1
            l = l + 1


    def watch_keyboard(self):
	    print("Starting to watch the keyboard, press Ctrl-C to exit")
	    while(True):
		msgs=[]
		r = self.device.read(8)
		if(r==[]):
		    continue
		print('[{}]'.format(', '.join(hex(x) for x in r)))
		# print(r)
                # print(r[2])
                try:
                    if((self.last_command[4] == 0x40) and (r[4] != 0x40)):
                        print("onHook")
                        if(self.delegate):
                            self.delegate.on_hook()
                    elif((self.last_command[4] != 0x40) and (r[4] == 0x40)):
                        print("offHook")
                        if(self.delegate):
                            self.delegate.off_hook()
                    elif((self.last_command[4] == 0x50) and (r[4] != 0x50)):
                        print("offSpeaker")
                        if(self.delegate):
                            self.delegate.off_speaker()
                    elif((self.last_command[4] != 0x50) and (r[4] == 0x50)):
                        print("onSpeaker")
                        if(self.delegate):
                            self.delegate.on_speaker()
                    # For whatever reason, sometimes I get 0x52 rather than 0x50
                    # for speaker
                    elif((self.last_command[4] == 0x52) and (r[4] != 0x52)):
                        print("offSpeaker")
                        if(self.delegate):
                            self.delegate.off_speaker()
                    elif((self.last_command[4] != 0x52) and (r[4] == 0x52)):
                        print("onSpeaker")
                        if(self.delegate):
                            self.delegate.on_speaker()
                    elif((self.last_command[4] == 0x60) and (r[4] != 0x60)):
                        print("offHeadphones")
                        if(self.delegate):
                            self.delegate.off_headphones()
                    elif((self.last_command[4] != 0x60) and (r[4] == 0x60)):
                        print("onHeadphones")
                        if(self.delegate):
                            self.delegate.on_headphones()
                    elif((self.last_command[7] == 0x01) and (r[7] != 0x01)):
                        print("offMute")
                        if(self.delegate):
                            self.delegate.off_mute()
                    elif((self.last_command[7] != 0x01) and (r[7] == 0x01)):
                        print("onMute")
                        if(self.delegate):
                            self.delegate.on_mute()
                    elif((self.last_command[2] == 0x00) and (r[2] != 0x00)):
                        print("keyDown")
                        self.time_last_key_down = time.time()
                        key = r[2]-1
                        print(key)
                        if(self.delegate):
                            self.delegate.key_down(key)
                    elif((self.last_command[2] != 0x00) and (r[2] == 0x00)):
                        print("keyUp")
                        time_key_was_pressed = time.time() - self.time_last_key_down
                        print(time_key_was_pressed)
                        key = self.last_command[2]-1
                        print(key)
                        if(self.delegate):
                            self.delegate.key_up(int(key), time_key_was_pressed)
                    elif(r[1] == 0x8):
                        print("longPress")
                        key = r[2]-1
                        print(key)
                        if(self.delegate):
                            self.delegate.long_press(key)
                    elif((self.last_command[1] == 0x00) and (r[1] != 0x00)):
                        key = r[1]
                        if(key==16): # Ignore Mute key, is handled elsewhere
                            continue
                        print("keyDown")
                        self.time_last_key_down = time.time()
                        if(key==4): # Redial
                            key=12
                        if(key==2): # Hold
                            key=13
                        if(key==32): # Backspace
                            key=14
                        print(key)
                        if(self.delegate):
                            self.delegate.key_down(key)
                    elif((self.last_command[1] != 0x00) and (r[1] == 0x00)):
                        key = self.last_command[1]
                        if(key==16): # Ignore Mute key, is handled elsewhere
                            continue
                        print("keyUp")
                        time_key_was_pressed = time.time() - self.time_last_key_down
                        print(time_key_was_pressed)
                        if(key==4): # Redial
                            key=12
                        if(key==2): # Hold
                            key=13
                        if(key==32): # Backspace
                            key=14
                        print(key)
                        if(self.delegate):
                            self.delegate.key_up(int(key), time_key_was_pressed)
                except:
                    pass
                print("")
                self.last_command = r

class Delegate:
    """Instead of this class, a consumer of this file could implement
    its functions and hence receive and act on the callbacks"""
    def on_hook(self):
        print("Delegate on_hook acting...")
    def off_hook(self):
        print("Delegate off_hook acting...")
    def on_speaker(self):
        print("Delegate on_speaker acting...")
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
        print("Delegate key_down(%i) acting..." % (key))
    def key_up(self, key, time_key_was_pressed):
        print("Delegate key_up(%i, %f) acting..." % (key, time_key_was_pressed))
    def long_press(self, key):
        print("Delegate long_press(%i) acting..." % (key))

def main():
    d = Delegate()
    c = CX300(d)

    c.display_two_lines("Welcome to CX300", "from Python")

    # Cycle through LED colors
    stati = [CX300.STATUS_LED_GREEN, CX300.STATUS_LED_RED, 
             CX300.STATUS_LED_ORANGE_RED, CX300.STATUS_LED_ORANGE,
             CX300.STATUS_LED_GREEN_ORANGE, CX300.STATUS_LED_OFF]
    for status in stati:
        time.sleep(0.2)
        c.device.write(status)

    # c.display_clear()
    c.display_two_lines("Press some keys", "on the CX300 öäüß") # Umlauts test

    try:
        c.watch_keyboard()
    except (KeyboardInterrupt, SystemExit):
        print '\n! Received keyboard interrupt, quitting\n'
        c.timer.stop()
        c.close()

    c.close()

if (__name__ == "__main__"):
    main()
