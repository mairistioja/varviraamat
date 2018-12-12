#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys #Qapplication tahab sys-i
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from xml.dom.minidom import parseString
import math
import re

# See funktsioon on litsenseeritud LGPL 2.0 litsentsiga,
#   Copyright (C) 2016 The Qt Company Ltd.it.
# vastavalt tingimustele KDE Free Qt Foundation tingimustele.
# Võetud aadressilt http://code.qt.io/cgit/qt/qtsvg.git/tree/src/svg/qsvghandler.cpp
def pathArcSegment(path, xc, yc, th0, th1, rx, ry, xAxisRotation):
    sinTh = math.sin(xAxisRotation * (math.pi / 180.0))
    cosTh = math.cos(xAxisRotation * (math.pi / 180.0))

    a00 =  cosTh * rx
    a01 = -sinTh * ry
    a10 =  sinTh * rx
    a11 =  cosTh * ry

    thHalf = 0.5 * (th1 - th0)
    t = (8.0 / 3.0) * math.sin(thHalf * 0.5) * math.sin(thHalf * 0.5) / math.sin(thHalf)
    x1 = xc + math.cos(th0) - t * math.sin(th0)
    y1 = yc + math.sin(th0) + t * math.cos(th0)
    x3 = xc + math.cos(th1)
    y3 = yc + math.sin(th1)
    x2 = x3 + t * math.sin(th1)
    y2 = y3 - t * math.cos(th1)

    path.cubicTo(a00 * x1 + a01 * y1, a10 * x1 + a11 * y1,
                 a00 * x2 + a01 * y2, a10 * x2 + a11 * y2,
                 a00 * x3 + a01 * y3, a10 * x3 + a11 * y3)

# See funktsioon on võetud järgneva litsentsiga:
#
# Copyright  2002 USC/Information Sciences Institute
#
# Permission to use, copy, modify, distribute, and sell this software
# and its documentation for any purpose is hereby granted without
# fee, provided that the above copyright notice appear in all copies
# and that both that copyright notice and this permission notice
# appear in supporting documentation, and that the name of
# Information Sciences Institute not be used in advertising or
# publicity pertaining to distribution of the software without
# specific, written prior permission.  Information Sciences Institute
# makes no representations about the suitability of this software for
# any purpose.  It is provided "as is" without express or implied
# warranty.
#
# INFORMATION SCIENCES INSTITUTE DISCLAIMS ALL WARRANTIES WITH REGARD
# TO THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS, IN NO EVENT SHALL INFORMATION SCIENCES
# INSTITUTE BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL
# DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA
# OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
# TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.
#
def pathArc(path, rx, ry, x_axis_rotation, large_arc_flag, sweep_flag, x, y, curx, cury):
    rx = abs(rx)
    ry = abs(ry)

    sin_th = math.sin(x_axis_rotation * (math.pi / 180.0))
    cos_th = math.cos(x_axis_rotation * (math.pi / 180.0))

    dx = (curx - x) / 2.0
    dy = (cury - y) / 2.0
    dx1 =  cos_th * dx + sin_th * dy
    dy1 = -sin_th * dx + cos_th * dy
    Pr1 = rx * rx
    Pr2 = ry * ry
    Px = dx1 * dx1
    Py = dy1 * dy1
    # Spec : check if radii are large enough 
    check = Px / Pr1 + Py / Pr2
    if (check > 1):
        rx = rx * math.sqrt(check)
        ry = ry * math.sqrt(check)

    a00 =  cos_th / rx
    a01 =  sin_th / rx
    a10 = -sin_th / ry
    a11 =  cos_th / ry
    x0 = a00 * curx + a01 * cury
    y0 = a10 * curx + a11 * cury
    x1 = a00 * x + a01 * y
    y1 = a10 * x + a11 * y
    # (x0, y0) is current point in transformed coordinate space.
    #   (x1, y1) is new point in transformed coordinate space.
    #
    #   The arc fits a unit-radius circle in this space.
    d = (x1 - x0) * (x1 - x0) + (y1 - y0) * (y1 - y0)
    sfactor_sq = 1.0 / d - 0.25
    if sfactor_sq < 0:
        sfactor_sq = 0
    sfactor = math.sqrt(sfactor_sq)
    if sweep_flag == large_arc_flag: 
        sfactor = -sfactor
    xc = 0.5 * (x0 + x1) - sfactor * (y1 - y0)
    yc = 0.5 * (y0 + y1) + sfactor * (x1 - x0)
    # (xc, yc) is center of the circle. 

    th0 = math.atan2(y0 - yc, x0 - xc)
    th1 = math.atan2(y1 - yc, x1 - xc)

    th_arc = th1 - th0
    if th_arc < 0 and sweep_flag:
        th_arc += 2 * math.pi
    elif th_arc > 0 and not sweep_flag:
        th_arc -= 2 * math.pi

    n_segs = math.ceil(abs(th_arc / (math.pi * 0.5 + 0.001)))

    for i in range(n_segs):
        pathArcSegment(path, xc, yc,
                       th0 + i * th_arc / n_segs,
                       th0 + (i + 1) * th_arc / n_segs,
                       rx, ry, x_axis_rotation)


class JoonistusAken(QMainWindow):
    def __init__(self): # self viitab klassile endale, init on konstruktor
        super().__init__() #konstrueerib superklassi
        self.setWindowTitle("Test") #akna pealkiri
        self.aktiivne_varv = QColor(0, 0, 0)

        # Menüüd:
        fileMenu = self.menuBar().addMenu("&File") #addMenu lisab alammenüü, & märgib alammenüü kiirendi, alt+F.
        openAction = QAction("&Open", self) #loob tegevuse, self on vajalik, et alles jääks
        openAction.setShortcut("Ctrl+O")
        openAction.triggered.connect(self.ava_fail) #signaal triggered käivitatakse siis, kui keegi QActioni käivitab (klikib vms).
        fileMenu.addAction(openAction) #paneb openActioni failimenüü lõppu
        quitAction = QAction("&Quit", self) #loob tegevuse, self on vajalik, et alles jääks
        quitAction.setShortcut("Ctrl+Q")
        quitAction.triggered.connect(self.close) #signaal triggered käivitatakse siis, kui keegi QActioni käivitab (klikib vms).
        fileMenu.addAction(quitAction) #paneb quitActioni failimenüü lõppu
        
        toolbar = self.addToolBar('maintoolbar')
        color_action = toolbar.addAction('Vali värv')
        color_action.triggered.connect(self.vali_varv)
        
        # Joonistusala:
        self.view = QGraphicsView(self) #Qgraphicsview on widget, mis kuvab joonistusala
        self.setCentralWidget(self.view) #paneb view QMainWindow keskseks vidinaks

        self.showMaximized() #teeb joonistusakna nähtavaks ja ekraani suuruseks

    def vali_varv(self):
        dialog = QColorDialog()
        dialog.setCurrentColor(self.aktiivne_varv)
        if dialog.exec() == 1:
            self.aktiivne_varv = dialog.currentColor()


    def ava_fail(self):
        failinimi, _ = QFileDialog.getOpenFileName(self, 'Ava joonistus', '/', 'Joonistused (*.svg)')
        if failinimi == '':
            return

        fail = open(failinimi)
        read = fail.readlines()
        while len(read) > 0 and read[-1].strip() == "":
            del read[-1]
        if re.match('^<!--värviraamat [^-]* -->$' ,read[-1].strip()):
            värvid = read[-1].strip()
            del read[-1]

        self.failisisu = "".join(read)
        svg = parseString(self.failisisu)
        uus_scene = QGraphicsScene(self)
        for kujund in svg.getElementsByTagName("path"):
            d = kujund.getAttribute("d")

            # teisendame loetavamale kujule
            d = re.sub("([MmLlHhVvAaCcSsQqTtZz])([-0-9.])", "\\1 \\2", d) #tühik vahele
            d = re.sub("([0-9.])([-MmLlHhVvAaCcSsQqTtZz])", "\\1 \\2", d) #tühik vahele
            d = re.sub("([MmLlHhVvAaCcSsQqTtZz])([-MmLlHhVvAaCcSsQqTtZz])", "\\1 \\2", d) #tühik vahele
            d = re.sub("[ ,]+", " ", d) #mitu tühikut ja/või koma üheks tühikuks

            d = d.split()
            print(d)
            e = JoonistusElement(self)
            p = QPainterPath()
            käsk = ""
            eelnev_käsk = ""
            argumente_vaja = {
                'M': 2, 'm': 2, 'L' : 2, 'l': 2, 'H': 1, 'h': 1, 'V': 1, 'v': 1, 'a': 7, 'A': 7, 'c': 6, 'C': 6, 'q': 4, 'Q': 4, 's': 4, 'S': 4, 't': 2, 'T': 2, 'z': 0, 'Z': 0
            }
            a = [] #argumendid
            viimanepunkt = [0.0, 0.0]
            for x in d:
                if len(a) == 0 and len(x) == 1 and x[0] in argumente_vaja.keys():
                    a = []
                    eelnev_käsk = käsk
                    käsk = x
                else:
                    if len(a) < argumente_vaja[käsk]:
                        a.append(x)
                    if len(a) >= argumente_vaja[käsk]:
                        if käsk == 'M':
                            viimanepunkt = [float(a[0]), float(a[1])]
                            p.moveTo(viimanepunkt[0], viimanepunkt[1])
                            käsk = 'L'
                        elif käsk == 'm':
                            viimanepunkt = [viimanepunkt[0] + float(a[0]), viimanepunkt[1] + float(a[1])]
                            p.moveTo(viimanepunkt[0], viimanepunkt[1])
                            käsk = 'l'
                        elif käsk == 'L':
                            viimanepunkt = [float(a[0]), float(a[1])]
                            p.lineTo(viimanepunkt[0], viimanepunkt[1])
                        elif käsk == 'l':
                            viimanepunkt = [viimanepunkt[0] + float(a[0]), viimanepunkt[1] + float(a[1])]
                            p.lineTo(viimanepunkt[0], viimanepunkt[1])
                        elif käsk == 'V':
                            viimanepunkt[1] = float(a[0])
                            p.lineTo(viimanepunkt[0], viimanepunkt[1])
                        elif käsk == 'v':
                            viimanepunkt[1] += float(a[0])
                            p.lineTo(viimanepunkt[0], viimanepunkt[1])
                        elif käsk == 'H':
                            viimanepunkt[0] = float(a[0])
                            p.lineTo(viimanepunkt[0], viimanepunkt[1])
                        elif käsk == 'h':
                            viimanepunkt[0] += float(a[0])
                            p.lineTo(viimanepunkt[0], viimanepunkt[1])
                        elif käsk == 'a' or käsk == 'A':
                            if käsk == 'a':
                                uuspunkt = [viimanepunkt[0] + float(a[5]), viimanepunkt[1] + float(a[6])]
                            else:
                                uuspunkt = [float(a[5]), float(a[6])]
                            pathArc(p, float(a[0]), float(a[1]), float(a[2]), (a[3] != '0'), (a[4] != '0'), uuspunkt[0], uuspunkt[1], viimanepunkt[0], viimanepunkt[1])
                            viimanepunkt = uuspunkt
                        elif käsk == 'c':
                            uuspunkt = [viimanepunkt[0] + float(a[4]), viimanepunkt[1] + float(a[5])]
                            viimanekontrollpunkt = (viimanepunkt[0] + float(a[2]), viimanepunkt[1] + float(a[3]))
                            p.cubicTo(viimanepunkt[0] + float(a[0]), viimanepunkt[1] + float(a[1]), viimanekontrollpunkt[0], viimanekontrollpunkt[1], uuspunkt[0], uuspunkt[1])
                            viimanepunkt = uuspunkt
                        elif käsk == 'C':
                            viimanepunkt = [float(a[4]), float(a[5])]
                            viimanekontrollpunkt = (float(a[2]), float(a[3]))
                            p.cubicTo(float(a[0]), float(a[1]), viimanekontrollpunkt[0], viimanekontrollpunkt[1], viimanepunkt[0], viimanepunkt[1])
                        elif käsk == 'Q':
                            viimanepunkt = [float(a[2]), float(a[3])]
                            p.quadTo(float(a[0]), float(a[1]), viimanepunkt[0], viimanepunkt[1])
                            viimanekontrollpunkt = (float(a[0]), float(a[1]))
                        elif käsk == 'q':
                            uuspunkt = [viimanepunkt[0] + float(a[2]), viimanepunkt[1] + float(a[3])]
                            p.quadTo(viimanepunkt[0] + float(a[0]), viimanepunkt[1] + float(a[1]), uuspunkt[0], uuspunkt[1])
                            viimanepunkt = uuspunkt
                            viimanekontrollpunkt = (viimanepunkt[0] + float(a[0]), viimanepunkt[1] + float(a[1]))
                        elif käsk == 'S':
                            if eelnev_käsk in ['c', 'C', 's', 'S']:
                                c1 = (2*viimanepunkt[0]-viimanekontrollpunkt[0], 2*viimanepunkt[1]-viimanekontrollpunkt[1])
                            else:
                                c1 = viimanepunkt
                            viimanepunkt = [float(a[2]), float(a[3])]
                            viimanekontrollpunkt = (float(a[0]), float(a[1]))
                            p.cubicTo(c1[0], c1[1], viimanekontrollpunkt[0], viimanekontrollpunkt[1], viimanepunkt[0], viimanepunkt[1]) 
                        elif käsk == 's':
                            if eelnev_käsk in ['c', 'C', 's', 'S']:
                                c1 = (2*viimanepunkt[0]-viimanekontrollpunkt[0], 2*viimanepunkt[1]-viimanekontrollpunkt[1])
                            else:
                                c1 = viimanepunkt
                            viimanekontrollpunkt = (viimanepunkt[0] + float(a[0]), viimanepunkt[1] + float(a[1]))
                            viimanepunkt = [viimanepunkt[0] + float(a[2]), viimanepunkt[0] + float(a[3])]
                            p.cubicTo(c1[0], c1[1], viimanekontrollpunkt[0], viimanekontrollpunkt[1], viimanepunkt[0], viimanepunkt[1])
                        elif käsk == 'T':
                            if eelnev_käsk in ['q', 'Q', 't', 'T']:
                                viimanekontrollpunkt = (2*viimanepunkt[0]-viimanekontrollpunkt[0], 2*viimanepunkt[1]-viimanekontrollpunkt[1])
                            else:
                                viimanekontrollpunkt = viimanepunkt
                            viimanepunkt = [float(a[0]), float(a[1])]
                            p.quadTo(viimanekontrollpunkt[0], viimanekontrollpunkt[1], viimanepunkt[0], viimanepunkt[1])
                        elif käsk == 't':
                            if eelnev_käsk in ['q', 'Q', 't', 'T']:
                                viimanekontrollpunkt = (2*viimanepunkt[0]-viimanekontrollpunkt[0], 2*viimanepunkt[1]-viimanekontrollpunkt[1])
                            else:
                                viimanekontrollpunkt = viimanepunkt
                            viimanepunkt = [float(a[0]), float(a[1])]
                            p.quadTo(viimanekontrollpunkt[0], viimanekontrollpunkt[1], viimanepunkt[0], viimanepunkt[1])
                        elif käsk == 'z' or käsk == 'Z':
                            p.closeSubpath()
                        a = [] #uuele ringile

                    
            e.setPath(p)
            uus_scene.addItem(e)
            self.scene = uus_scene
            self.view.setScene(uus_scene)

class JoonistusElement(QGraphicsPathItem):
    def __init__(self, peaaken):
        super().__init__()
        self.peaaken = peaaken
        self.setPen(QPen(Qt.NoPen))
        self.setBrush(QColor(0, 0, 0))
        
    def mousePressEvent(self, event): #seda kutsutakse välja, kui keegi vajutab QGraphicsPathItemi peale, event-i sees on tõenäol sündmuse info
        self.setBrush(self.peaaken.aktiivne_varv)
        return QGraphicsPathItem.mousePressEvent(self, event) #päris kindel ei ole, kas seda on vaja, aga vist on hea stiil

app = QApplication(sys.argv)
rakendus = JoonistusAken()
app.exec_() #Enters the main event loop and waits until exit() is called. The main event loop receives events from the window system and dispatches these to the application widgets.
