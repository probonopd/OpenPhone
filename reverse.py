#!/usr/bin/env python

from config import config

from lxml import html # apt install python-lxml
import requests # apt install python-requests
import os, sys, shutil, json, configparser, re

import fritz

# Currently this file is implemented for Germany (in German) only
# but it should give you an idea what to implement for your country

countries_json_file = os.path.dirname(__file__)+"/countries.json"
if not(os.path.isfile(countries_json_file)):
    url = "http://restcountries.eu/rest/v2/all?fields=callingCodes;name;translations"
    print("Downloading %s" % (url))
    r = requests.get(url, allow_redirects=True, timeout=3)
    open(countries_json_file, 'wb').write(r.content)

def get_country_name(number, language="en"):
    number=number.lstrip("0") # remove leading zeros
    language=language.split("-")[0]
    fp = open(countries_json_file,"r")
    json_object = json.load(fp)
    for country in json_object:
        for calling_code in country["callingCodes"]:
            if(calling_code == ""):
                continue
            if(number.startswith(calling_code)):
                if(language in ["br", "pt", "nl", "hr", "fa", "de", "es", "fr", "ja", "it"]):
                    return(country["translations"][language])
                else:
                    return(country["name"])
    fp.close()
    return(None)

def telefonbuch_reverse(number):
    if not(number.startswith("0049")):
        return None
    number = "0" + number[4:]
    url = "https://www.dastelefonbuch.de/R%C3%BCckw%C3%A4rts-Suche/" + number
    print(url)
    page = requests.get(url, timeout=3)
    tree = html.fromstring(page.content)
    try:
        name = tree.xpath('//span[@itemprop="name"]/text()')[0]
    except:
        return(None)
    try:
        location = tree.xpath('//span[@itemprop="addressLocality"]/text()')[0]
    except:
        location=None
    if(location==None):
        """Some entries in telefonbuch.de do not have a location; for these we try to resolve to a location using tellows"""
        try:
            location = tellows_reverse(number).split(" aus ")[1].split(" von ")[0]
        except:
            pass
    name = " ".join(re.split("\s+", name, flags=re.UNICODE)).strip() # Remove whitespace
    location = " ".join(re.split("\s+", location, flags=re.UNICODE)).strip() # Remove whitespace
    # print(name)
    # print(location)
    if(location):
        return("Anruf von %s aus %s" % (name, location))
    else:
        return("Anruf von %s" % (name))

def tellows_reverse(number):
    # number = "0" + number[4:]
    url = "http://www.tellows.de/basic/num/"+number+"?json=1&partner=test&apikey=test123"
    # print(url)
    resp = requests.get(url=url, params=None, timeout=3)
    data = resp.json()
    # print(data)
    # print(data["tellows"]["location"])
    if(int(data["tellows"]["score"]) > 7):
        return("Werbeanruf aus %s" % (data["tellows"]["location"]))
    else:
        number_without_prefix = data["tellows"]["normalizedNumber"].split("-")[1]
        return("Anruf aus %s von %s" % (data["tellows"]["location"], number_without_prefix))

def fritz_reverse(number):
    F = fritz.FritzBox(host=config['fritzbox0']['host'], password=config['fritzbox0']['password'])
    reversed = F.reverse(number)
    if(reversed != None):
        return("Anruf von %s" % (reversed))

def normalize_number(number):
    number = number.replace("+", config['Phone']['international_call_prefix'])
    number = "".join(i for i in number if i in "0123456789")
    print(number)
    # Normalize number to 0049... format    
    if((number.startswith("0")) and not (number.startswith(config['Phone']['international_call_prefix']))):
        number = config['Phone']['international_call_prefix'] + config['Phone']['country_code'] + number.lstrip("0")
    elif(not(number.startswith("0"))):
        number = config['Phone']['international_call_prefix'] + config['Phone']['country_code'] + config['Phone']['local_prefix'] + number
    return(number)

def reverse(number, language="en"):
    """Reverses the number. It is important to wrap this in "try:" so that it never fails, even if we cannot reverse the number"""
    try:
        print("############################## Reversing %s" % (str(number)))
        if not((number.startswith("0")) or (number.startswith(config['Phone']['international_call_prefix']))):
		fb = fritz_reverse(number)
		if(fb != None):
		    return(fb)
        normalized_number = normalize_number(number)

        if(normalized_number.startswith(config['Phone']['international_call_prefix'] + "49")):
            fb = fritz_reverse(normalized_number.replace(config['Phone']['international_call_prefix'] + "49", "0"))
            if(fb != None):
                 return(fb)
            tb = telefonbuch_reverse(normalized_number)
            if(tb != None):
                 return(tb)
            else:
                 return(tellows_reverse(normalized_number))
        else:
            return(tellows_reverse(normalized_number))
    except:
        return(number)

if(__name__=="__main__"):

    if len(sys.argv) >= 2:
        print(reverse(sys.argv[1]))
    else:
        print(reverse("+1 917-275-6975", "de-DE"))
        print(reverse("+41 22 917 12 34", "de-DE"))
        print(reverse("089473737350", "de-DE"))
        print(reverse("**620"))
        print(reverse("62041"))