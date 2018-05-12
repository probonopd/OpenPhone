#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import termios
import contextlib

class Keyboard():
    """Minimal implementation to use an attached USB keyboard as an input. Detection of long-presses is not implemented yet."""

    def __init__(self, delegate=None):
        self.time_last_key_down = None
        if(delegate):
            self.delegate = delegate

    @contextlib.contextmanager
    def raw_mode(self,file):
        old_attrs = termios.tcgetattr(file.fileno())
        new_attrs = old_attrs[:]
        new_attrs[3] = new_attrs[3] & ~(termios.ECHO | termios.ICANON)
        try:
            termios.tcsetattr(file.fileno(), termios.TCSADRAIN, new_attrs)
            yield
        finally:
            termios.tcsetattr(file.fileno(), termios.TCSADRAIN, old_attrs)


    def listen_keys(self):
        print 'exit with ^C or ^D'
        with self.raw_mode(sys.stdin):
            try:
                while True:
                    ch = sys.stdin.read(1)
                    if not ch or ch == chr(4):
                        break
                    print '%02x' % ord(ch)
                    if ch in ["0","1","2","3","4","5","6","7","8","9","*","#"]:
                        if(ch=="*"):
                            ch=11
                        if(ch=="#"):
                            ch=12
                        self.delegate.key_up(int(ch),0.001)
                    elif(ch == "a"):
                        print("Answer")
                    elif(ord(ch) == 0x1b):
                        self.delegate.on_hook()
                    elif(ord(ch) == 0x0a):
                        self.delegate.off_hook()
            except (KeyboardInterrupt, EOFError):
                pass

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


if __name__ == '__main__':
    D = Delegate()
    K = Keyboard(D)
    K.listen_keys()
