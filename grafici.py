#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-

from pygooglechart import Chart
from pygooglechart import SimpleLineChart
from pygooglechart import XYLineChart
from pygooglechart import SparkLineChart
from pygooglechart import Axis
from pygooglechart import GroupedVerticalBarChart
from pygooglechart import PieChart3D

import sqlite3
import datetime
conn=sqlite3.connect("/home/glisha/webapps/nginx_domejnotmk/domejnotmk/soberipodatoci/domejni.sqlite3")

def novidomejni_grafik():
    """По датум последните 30 дена колку нови домејни имало."""

    c1 = conn.cursor()
    c1.execute("select datum, novidomejni from novidomejni order by datum desc limit 30")

    novi = [x for x in c1]
    novi.sort()

    datumi = [x[0] for x in novi]
    ipsilonoska = [int(x[1]) for x in novi] # kolku novi
    iksoska = [x for x in range(0,len(datumi))]

    xmax = len(iksoska)
    ymax = max([int(a[1]) for a in novi])

    chart = XYLineChart(800,300,x_range=(0,xmax-1),y_range=(0,ymax))

    chart.add_data(iksoska)
    chart.add_data(ipsilonoska)

    for x in range(0,len(datumi)):
        if x%2:
            datumi[x]=''

    ipsilon = [ x for x in range(0,ymax+1)]
    for y in range(0,ymax+1):
        if y%2:
            ipsilon[y]=''
    ipsilon[0]=''
    ipsilon[-1]=ymax

    chart.set_axis_labels(Axis.BOTTOM,datumi)
    chart.set_axis_labels(Axis.LEFT, ipsilon)
    chart.set_title("Број на нови .mk домени по денови|")

    return chart.get_url()

def tipovidomejn_grafik():
    """Вкупно колку домејни има по типови"""

    c2 = conn.cursor()
    tipovi = {'.com.mk':0,'.org.mk':0,'.gov.mk':0,'.name.mk':0,'.net.mk':0,'.inf.mk':0,'.edu.mk':0}

    vchera = (datetime.datetime.now() - datetime.timedelta(1)).date()
    c2.execute("select count(distinct domejn) from domejni where datum=?",(vchera.strftime("%Y-%m-%d"),))
    vkupno = c2.fetchone()[0]

    ostanati = 0
    for tip,broj in tipovi.iteritems():
        c2.execute("select count(distinct domejn) from domejni where datum=? and domejn like ?",(vchera.strftime("%Y-%m-%d"),'%%%s' % tip))
        tipovi[tip]=c2.fetchone()[0]
        ostanati+=tipovi[tip]

    tipovi['.mk']=vkupno-ostanati

    chart = PieChart3D(500, 200)
    chart.add_data([x for x in tipovi.itervalues()])
    chart.set_pie_labels(["%s (%s%%)" % (x,round(y*100.0/vkupno,2)) for x,y in tipovi.iteritems()])


    chart.set_legend(["%s (%s)" % (x,y) for x,y in tipovi.iteritems()])
    chart.set_legend_position('b')
    chart.set_title("Вкупно %s .мк домени од кои:" % vkupno)

    return chart.get_url()

