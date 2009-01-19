#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-

import datetime
import sqlite3
import pickle
import urllib2
import BeautifulSoup
import codecs
import cgi

format_na_datum="%Y-%m-%d"# %H:%M:%S"
deneska = datetime.datetime.now().date()

def stranici():
    """Листата со линкови од http://dns.marnet.net.mk/registar.php"""
    fajl = open('/home/glisha/webapps/nginx_domejnotmk/domejnotmk/soberipodatoci/domejni_stranici.pckl','rb')
    stranici = pickle.load(fajl)
    fajl.close()
    return stranici

def zemi_domejni(stranici):
    """Ги зима домејните од Марнет. stranici треба да е ажурна
    листа на страници од главната страница на Марнет."""

    #ako deneska sum sobral ne probuvaj pak
    conn = sqlite3.connect("/home/glisha/webapps/nginx_domejnotmk/domejnotmk/soberipodatoci/domejni.sqlite3")
    c = conn.cursor()
    c.execute('select count(*) from domejni where datum=?',(deneska,))
    if c.fetchone()[0]<>0:
        return []

    domejni = []
    for link in stranici:
        #print u"Го обработувам %s" % link

        req = urllib2.Request(u'http://dns.marnet.net.mk/' + link)
        res = urllib2.urlopen(req)
        strana = res.read()
        soup = BeautifulSoup.BeautifulSoup(strana)

        domejn_linkovi = soup.findChildren('a',{'class':'do'})

        for domejn in domejn_linkovi:
            if domejn['href'].find('dom=')<>-1:
                domejni.append(domejn['href'].replace('registar.php?dom=',''))

    return domejni
    

def sochuvaj_domejni(domejni):
    """Ги сочувува домејните во база"""

    if not domejni:
        return False

    conn = sqlite3.connect("/home/glisha/webapps/nginx_domejnotmk/domejnotmk/soberipodatoci/domejni.sqlite3")
    c = conn.cursor()

    for domejn in domejni:
        c.execute("insert into domejni values (?,?)",(deneska,domejn))

    conn.commit()
    c.close()

def novi_domejni(datumstar,datumnov):
    """Кои домејни ги има во datumnov а ги нема во datumstar."""

    conn = sqlite3.connect("/home/glisha/webapps/nginx_domejnotmk/domejnotmk/soberipodatoci/domejni.sqlite3")
    c = conn.cursor()
    
    c.execute("""
            select 
                datum,domejn 
            from 
                domejni 
            where 
                datum=? and 
                domejn not in (select domejn from domejni where datum=?)""",
            (datumnov.strftime("%Y-%m-%d"),datumstar.strftime("%Y-%m-%d")))

    a = [(novdomejn[0],novdomejn[1]) for novdomejn in c]

    c.execute("select count(*) from novidomejni where datum=?",(datumstar.strftime("%Y-%m-%d"),))
    if c.fetchone()[0]==0:
        c.execute("insert into novidomejni values (?,?)",(datumstar.strftime("%Y-%m-%d"),len(a)))
        conn.commit()

    c.close()
    return a

def format_date(dt):
    """convert a datetime into an RFC 822 formatted date

        Input date must be in GMT.
    """
    # Looks like:
    #   Sat, 07 Sep 2002 00:00:01 GMT
    # Can't use strftime because that's locale dependent
    #
    # Isn't there a standard way to do this for Python?  The
    # rfc822 and email.Utils modules assume a timestamp.  The
    # following is based on the rfc822 module.
    return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (
                ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][dt.weekday()],
                dt.day,
                ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                 "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][dt.month-1],
                dt.year, dt.hour, dt.minute, dt.second)

def output_html(novidomejni):
    if not novidomejni:
        return

    import grafici
    podatum_grafik = grafici.novidomejni_grafik()
    potip_grafik = grafici.tipovidomejn_grafik()

    fajl = codecs.open("/home/glisha/webapps/nginx_domejnotmk/domejnotmk/public_html/index.html","w","utf-8")
    fajl.write(u"""<html>
        <head>
        <title>Ново регистрирани домејни денеска</title>
        <meta http-equiv="content-type" content="text/html; charset=utf-8">
        <meta name="Author" content="Georgi Stanojevski <http://isengard.unet.com.mk/~georgi/ueb/>">
        <link rel="shortcut icon" href="favicon.ico" />
        <link rel="alternate" type="application/rss+xml" title="Најнови домејни" href="/novidomejni.xml" />
        <style>
            body { 
            font-family: sans-serif;
            }
        </style>
    </head><body>
    <p>&nbsp;</p>
    <p><b>Претплати се на <a href='/novidomejni.xml'>RSS каналот</a> за веднаш да дознаваш кои се новo регистрирани .mk домејни.</b></p>
    <p>Ново регистрирани домејни:</p>""")

    fajl.write(u"<ul>")
    for element in novidomejni:
        fajl.write(u"<li><a title='Опис во Марнет' href='http://dns.marnet.net.mk/registar.php?dom=%s'>%s</a> (<a href='http://www.%s' title='Кон сајтот'><img border=0 src='/external.png' /></a>)</li>" % (element[1],element[1],element[1]))

    fajl.write(u"</ul>")

    fajl.write(u'<center><img src="%s" alt="Novi domejni poslednite 30 denovi" /></center><br /><br /><br />' % podatum_grafik)
    fajl.write(u'<center><img src="%s" alt="Registrirani .mk domeni po tip" /></center><br /><hr />' % potip_grafik)
    fajl.write(u'<p>Архивата е <a href="/podatum/">тука</a>, скриптите со кои се генерира <a href="/novimkdomejni.tar.gz">тука</a>, останати работи на <a href="http://isengard.unet.com.mk/~georgi/ueb/">http://isengard.unet.com.mk/~georgi/ueb/</a></p></body></html>')


def output_rss(novidomejni):
    """RSS со новите. Ако нема нови не го чепка старото рсс."""
    if not novidomejni:
        return


    fajl = codecs.open("/home/glisha/webapps/nginx_domejnotmk/domejnotmk/public_html/novidomejni.xml","w","utf-8")
    fajl.write(u"""<?xml version="1.0" encoding="utf-8"?>
                        <rss version="2.0">
                        <channel>
                        <title>Нови .мк домејни</title>
                        <link>http://domejn.ot.mk</link>
                        <description>Листа на ново регистрираните домејни денеска.</description>
                        <language>mk</language>
                        <image>
                        <title>Нови .мк домејни</title>
                        <url>mk.jpg</url>
                        <link>http://domejn.ot.mk</link>
                        </image>\n""")

    for element in novidomejni:
        fajl.write("""<item>
                            <title>%s</title>
                            <link>http://dns.marnet.net.mk/registar.php?dom=%s</link>
                            <description>&lt;a href=&quot;http://www.%s&quot;&gt;%s&lt;/&gt;</description>
                            <pubDate>%s</pubDate>
                            <guid>http://dns.marnet.net.mk/registar.php?dom=%s</guid>
                            </item>""" % 
                (element[1],
                element[1],
                element[1],
                element[1],
                format_date(datetime.datetime.strptime(element[0],'%Y-%m-%d')),
                element[1]))

    fajl.write("</channel></rss>")
    fajl.close()



if __name__=="__main__":
    stranici = stranici()
    domejni = zemi_domejni(stranici)

    if domejni:
        sochuvaj_domejni(domejni)

        datumstar = datetime.datetime.now().date() - datetime.timedelta(1)
        datumnov = datetime.datetime.now().date()
        novi = novi_domejni(datumstar,datumnov)
        if novi:
            import shutil
            shutil.copyfile("/home/glisha/webapps/nginx_domejnotmk/domejnotmk/public_html/index.html","/home/glisha/webapps/nginx_domejnotmk/domejnotmk/public_html/podatum/%s.html" % datumstar.strftime("%Y%m%d"))
            output_rss(novi)
            output_html(novi)
