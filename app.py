# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
from pytube import YouTube
import sys


class Ui_Form(object):
    def get_path(self,pathcomplet):
        liste_chemin = pathcomplet.split("/")
        titre = liste_chemin[-1]
        chemin = "/".join(liste_chemin[:-1]) + "/"
        return chemin , titre

    def fonction(self) :
        try:
            lien = self.input.text()
            youtube = YouTube(lien)
            titre = youtube.title + ".mp4"
        except:
            self.finish.setText("Un problème à eu lieu, l'url semble être incorrecte.")
        try:
            pathcomplet, _ = QFileDialog.getSaveFileName(None,'Save your video', titre, "mp4 vidéo (*.mp4);;All Files (*)")
            pathfile_finale , titre = self.get_path(pathcomplet)
            self.get_path(pathcomplet)
            video = youtube.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download(output_path=pathfile_finale,filename=titre)
            self.finish.setText("Votre téléchargement est fini !")
        except:
            self.finish.setText("Un probleme à eu lieu lors du téléchargement !.")

    def setupUi(self, Form):
        Form.setObjectName("Yt Downloader")
        Form.setWindowIcon(QtGui.QIcon('logo.jpg'))
        Form.resize(971, 821)
        font = QtGui.QFont()
        font.setPointSize(24)
        Form.setFont(font)
        self.titre = QtWidgets.QLabel(Form)
        self.titre.setGeometry(QtCore.QRect(320, 160, 303, 93))
        font = QtGui.QFont()
        font.setFamily("Onyx")
        font.setPointSize(50)
        self.titre.setFont(font)
        self.titre.setObjectName("titre")
        self.download = QtWidgets.QPushButton(Form)
        self.download.setGeometry(QtCore.QRect(350, 360, 511, 37))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.download.setFont(font)
        self.download.setObjectName("download")
        self.download.clicked.connect(self.fonction)
        self.input = QtWidgets.QLineEdit(Form)
        self.input.setGeometry(QtCore.QRect(350, 320, 511, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.input.setFont(font)
        self.input.setObjectName("input")
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(10, 320, 328, 24))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(180, 460, 576, 28))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.finish = QtWidgets.QLabel(Form)
        self.finish.setGeometry(QtCore.QRect(20, 520, 761, 48))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.finish.setFont(font)
        self.finish.setText("")
        self.finish.setObjectName("finish")
        self.label_4 = QtWidgets.QLabel(Form)
        self.label_4.setGeometry(QtCore.QRect(90, 120, 200, 159))
        self.label_4.setText("")
        self.label_4.setPixmap(QtGui.QPixmap("logo.jpg"))
        self.label_4.setObjectName("label_4")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Yt Downloader"))
        self.titre.setText(_translate("Form", "YT Downloader"))
        self.download.setText(_translate("Form", "Download"))
        self.label.setText(_translate("Form", "Entrez le lien de votre vidéo youtube"))
        self.label_2.setText(_translate("Form", "Si votre système se bloque, attendez quelques secondes."))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
