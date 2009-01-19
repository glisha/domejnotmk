#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Зима колку страници со домејни има секоја буква да може да ги посетам само тие линкови.
"""

import urllib2,urllib,pickle
from BeautifulSoup import BeautifulSoup

bukvi = ['NUM','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']

url = 'http://dns.marnet.net.mk/registar.php'

linkovi = []
for bukva in bukvi:
    #print "Глеам колку страници има на буква: %s" % bukva
    bukva = urllib.urlencode({'bukva':bukva})
    req = urllib2.Request(url,bukva)
    res = urllib2.urlopen(req)

    stranica = res.read()

    soup = BeautifulSoup(stranica)
    rawlinkovi = soup.findChildren('a',{'class':'do'})

    for link in rawlinkovi:
        if link['href'].find('del=') <> -1:
            linkovi.append(link['href'])

f = open('/home/glisha/webapps/nginx_domejnotmk/domejnotmk/soberipodatoci/domejni_stranici.pckl','wb')
pickle.dump(linkovi,f)
f.close()

#import pprint
#pprint.pprint(linkovi)
