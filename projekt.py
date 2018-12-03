#!/usr/bin/python
import sys #Qapplication tahab sys-i
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from xml.dom.minidom import parse
import math


def pathArcSegment(path, xc, yc, th0, th1, rx, ry, xAxisRotation): #the arc handling code underneath is from XSVG (BSD license)
# Copyright  2002 USC/Information Sciences Institute http://code.qt.io/cgit/qt/qtsvg.git/tree/src/svg/qsvghandler.cpp
    sinTh = math.sin(xAxisRotation * (pi / 180.0))
    cosTh = math.cos(xAxisRotation * (pi / 180.0))

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


def pathArc(path, rx, ry, x_axis_rotation, large_arc_flag, sweep_flag, x, y, curx, cury): #the arc handling code is from XSVG (BSD license)
# Copyright  2002 USC/Information Sciences Institute
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

        # Menüüd:
        fileMenu = self.menuBar().addMenu("&File") #addMenu lisab alammenüü, & märgib alammenüü kiirendi, alt+F.
        quitAction = QAction("&Quit", self) #loob tegevuse, self on vajalik, et alles jääks
        quitAction.setShortcut("Ctrl+Q")
        quitAction.triggered.connect(self.close) #signaal triggered käivitatakse siis, kui keegi QActioni käivitab (klikib vms).
        fileMenu.addAction(quitAction) #paneb quitActioni failimenüü lõppu
        
        # Joonistusala:
        self.scene = QGraphicsScene(self) #loob joonistusala
        view = QGraphicsView(self.scene, self) #Qgraphicsview on widget, mis kuvab joonistusala
        self.setCentralWidget(view) #paneb view QMainWindow keskseks vidinaks

        self.avafail("lind.svg")


        # Joonistus:
        e = JoonistusElement()
        imelik = QPainterPath() #The QPainterPath class provides a container for painting operations, enabling graphical shapes to be constructed and reused.
        imelik.addEllipse(0, 25, 100, 50) #nt teeb ellipsi
        imelik.moveTo(12,2)
        imelik.lineTo(100, 100)
        imelik.lineTo(20, 140)
        imelik.closeSubpath()
        e.setPath(imelik) #lisab/asendab joonistusElemendile
        self.scene.addItem(e)
        
        self.showMaximized() #teeb joonistusakna nähtavaks ja ekraani suuruseks

    def avafail(self, failinimi):
        fail = parse(failinimi)
        eraldi = []
        for kujund in fail.getElementsByTagName("path"):
            d = kujund.getAttribute("d").split()
            eraldi.append(d)
            e = JoonistusElement()
            p = QPainterPath()
            käsk = ""
            viimanepunkt = [0.0, 0.0]
            for x in d:
                if len(x) == 1:
                    if x == 'z':
                        p.closeSubpath()
                    else:
                        käsk = x
                else:
                    k = x.split(",")
                    k[0] = float(k[0])
                    k[1] = float(k[1])
                    if käsk == 'M':
                        p.moveTo(k[0], k[1])
                        viimanepunkt = k
                        käsk = 'L'
                    elif käsk == 'm':
                        viimanepunkt = [viimanepunkt[0] + k[0], viimanepunkt[1] + k[1]]
                        p.moveTo(viimanepunkt[0], viimanepunkt[1])
                        käsk = 'l'
                    elif käsk == 'L':
                        p.lineTo(k[0], k[1])
                        viimanepunkt = k
                    elif käsk == 'l':
                        viimanepunkt = [viimanepunkt[0] + k[0], viimanepunkt[1] + k[1]]
                        p.lineTo(viimanepunkt[0], viimanepunkt[1])
                    
                    
            e.setPath(p)
            self.scene.addItem(e)
        print(eraldi)   

class JoonistusElement(QGraphicsPathItem):
    def __init__(self):
        super().__init__()
        self.rgb = 'R'; #rgb on hetkel suvaline muutuja, mis kuulub joonistuselemendi sisse
        self.setPen(QPen(Qt.NoPen))
        self.setBrush(QColor(255, 0, 0))
        
    def mousePressEvent(self, event): #seda kutsutakse välja, kui keegi vajutab QGraphicsPathItemi peale, event-i sees on tõenäol sündmuse info
        if self.rgb == 'R':
            self.rgb = 'G'
            self.setBrush(QColor(0, 255, 0))
        elif self.rgb == 'G':
            self.rgb = 'B'
            self.setBrush(QColor(0, 0, 255))
        elif self.rgb == 'B':
            self.rgb = 'R'
            self.setBrush(QColor(255, 0, 0))
        return QGraphicsPathItem.mousePressEvent(self, event) #päris kindel ei ole, kas seda on vaja, aga vist on hea stiil

app = QApplication(sys.argv)
rakendus = JoonistusAken()
app.exec_() #Enters the main event loop and waits until exit() is called. The main event loop receives events from the window system and dispatches these to the application widgets.
