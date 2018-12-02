#!/usr/bin/python
import sys #Qapplication tahab sys-i
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from xml.dom.minidom import parse


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

        self.avafail("joonistus.svg")


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
        for kujund in fail.getElementsByTagName("path"):
            print(kujund.getAttribute("d"))

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
