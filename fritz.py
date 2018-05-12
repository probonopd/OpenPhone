#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

# Based on
# https://www.heise.de/forum/c-t/Kommentare-zu-c-t-Artikeln/Fritzbox-per-Skript-fernsteuern/AddPortMapping-mit-Python-funktioniert-nicht/thread-5065307/#posting_29394473

import requests, sys, re, os
from requests.auth import HTTPDigestAuth
import xml.etree.ElementTree as ElementTree

class FritzBox(object):
    def __init__(self, host="fritz.box", password=""):
        self.saction = "GetPhoneBook"
        self.sservice  = "urn:dslforum-org:service:X_AVM-DE_OnTel:1"
        self.controlURL = "upnp/control/x_contact"
        self.sparameter = """<NewPhonebookID>0</NewPhonebookID>""" 
        self.user = ''
        self.password = password
        self.host  = "http://" + host + ":49000/" # FIXME: Implement https
        self.phonebook_file = '/tmp/fritz_pbook.xml'
    
    def build_soap(self):
        req = u"""<?xml version="1.0"?>
            <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"
            s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
            <s:Body> 
            <u:{action} xmlns:u={service}>
            {parameter}
            </u:{action}>
            </s:Body>
            </s:Envelope>""".format(action=self.saction, service='\"'+self.sservice+'\"', parameter=self.sparameter)
        return  req.encode('utf-8')
    
    def post_soap(self):
        headers = {"Content-Type":'text/xml; charset="utf-8"',
                "SOAPAction": self.sservice+'#'+self.saction}
        response = requests.post(
                    url     = self.host + self.controlURL,
                    headers = headers,
                    data    = self.build_soap(),
                    auth    = HTTPDigestAuth(self.user, self.password),
                    verify  = False) 
        if not response.ok:
            return (False)   
        return response
     
    def response_to_xml_dict(self, tag, out=True):
        response = self.post_soap()
        try:
            if not response.ok:
                print 'HTTP error:', response
                return(None)
        except:
            print 'Error: invalid return value. Is the password correct?'
            print(response)
            return(None)
        if not out: return response.ok  
        response = response.content.replace("&lt;", "<").replace("&gt;", ">")
        response = response.replace("<s:", "<").replace("</s:", "</")
        response = response.replace("<u:", "<").replace("</u:", "</") 
        xml = '<?xml version="1.0" ?>'
        xml += response[response.find('<'+tag+'>'):response.find('</'+tag+'>')+len(tag)+3] 
        tree = ElementTree.ElementTree(ElementTree.fromstring(xml)) 
        tag_dict = tree.getroot() 
        return tag_dict
    
    def download_phonebook(self):   
        url = self.response_to_xml_dict('Body')[0].find('NewPhonebookURL').text
        r = requests.get(url, verify = False)
        if r.ok:
            try:
                f = open(self.phonebook_file, 'w')
                f.write(r.content)
                f.close()
                print("Downloaded phone book from Fritz!Box")
            except:
                print('Error writing file')
                return(None)           

    def reverse(self, number):
        print("Fritz reversing %s" % (number))
        if not(os.path.isfile(self.phonebook_file)):
            self.download_phonebook()
        tree = ElementTree.parse(self.phonebook_file)
        root = tree.getroot()
            
        for contact in root[0].findall('contact'):
            found_name = contact.find('person').find('realName').text
            found_number = contact.find('telephony').find('number').text
            if(number == found_number):
                return(found_name)
        return(None)

    def get_phonebook_csv(self):
        tree = ElementTree.parse(self.phonebook_file)
        root = tree.getroot()
            
        for contact in root[0].findall('contact'):
            rank = contact.find('person').find('realName').text
            name = contact.find('telephony').find('number').text
            print(("%s;%s") % (name, rank))
        
if(__name__ == "__main__"):
    F = FritzBox(password="...")
    F.download_phonebook()
    F.get_phonebook_csv()
