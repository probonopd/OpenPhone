# Features

## Audio

- [ ] Run amixer to set initial volume
- [ ] Make volume settable, including extra volume from pjsip

## User interface hardware

- [x] Read from CX300 keyboard
- [ ] Read from generic keyboard
- [ ] Read from IR remote control
- [x] Write to CX300 display
- [ ] Write to i2c display
- [ ] Physical quick dial (name) keys

## User interface software

- [ ] Clear text meaning of SIP codes in display https://de.wikipedia.org/wiki/SIP-Status-Codes
- [ ] Automatically dial (by just entering numbers and nothing else like on an analog/ISDN phone)
- [ ] Print each missed call on paper or put it on web interface or read it out aloud

## Ringtones

- [x] Play ringtone when we answer the incoming call with 180/Ringing
- [x] Play ringback tone (in Germany according to the 1TR110 standard)
- [x] Play busy tone (in Germany according to the 1TR110 standard)
- [ ] Play dialtone (in Germany according to the 1TR110 standard)

## Phone number lookup

- [x] Show calling number and reverse information on screen
- [x] Reverse search in dastelefonbuch.de
- [ ] Reverse search in local address book
- [x] Reverse search in Fritz!Box address book https://avm.de/fileadmin/user_upload/Global/Service/Schnittstellen/X_contactSCPD.pdf
- [x] If we don't find a match, identify at least the city
- [x] Play it back spoken as part of the ringtone -- killer feature! "Call from Munich"
- [x] Automatically warn if a number has a high Tellows score (spam call/"Werbeanruf") http://www.tellows.de/basic/num/004932214219001?json=1&partner=test&apikey=test123
- [ ] Cache Tellows results for a certain time

## Text-to-speech

- [x] Say each number during dialing
- [x] Say reversed number when dialing it ("Calling John Doe in Chicago")
- [x] Get vocalizations on the fly using libttspico-utils

## Speech-to-text

- [ ] React to voice commands
- [ ] Voice menus

## Other telephony features

- [ ] Use SRTP and TLS (some providers, e.g., easybell support it)
- [ ] Mailbox
- [ ] Call recording
- [ ] Immediately answer internal calls (optionally)
- [ ] Immediately send spam calls to mailbox (based on Tellows score)
- [ ] Presence, https://github.com/chakrit/pjsip/blob/master/pjsip-apps/src/python/samples/presence.py
- [ ] Tell who had called when user was not here

## Non-telephony features

- [ ] Webradio (mpd)
- [ ] Automatically mute (using IR) the TV and radio in the room when call comes in
