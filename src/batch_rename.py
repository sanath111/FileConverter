#!/usr/bin/python2
# *-* coding: utf-8 *-*
__author__ = "Sanath Shetty K"
__license__ = "GPL"
__email__ = "sanathshetty111@gmail.com"


import debug
import argparse
import glob
import os
import sys
import re
import pexpect
import setproctitle
try:
    from PyQt5.QtWidgets import QApplication, QFileSystemModel, QListWidgetItem
    from PyQt5 import QtCore, uic, QtGui, QtWidgets
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
except:
    pass

projDir = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-2])
sys.path.append(projDir)

main_ui_file = os.path.join(projDir, "uiFiles", "batch_rename.ui")
debug.info(main_ui_file)

imageFormats = ['png','exr','PNG','EXR','jpg','JPEG']
videoFormats = ['mov','mp4','MP4','avi','mkv']

parser = argparse.ArgumentParser(description="Use the comand to open a sandboxed UI for folders in an Asset")
parser.add_argument("-a","--asset",dest="asset",help="colon separated Asset path")
parser.add_argument("-p","--path",dest="path",help="Absolute path of the asset on disk")
parser.add_argument("-c","--close",dest="close",action="store_true",help="Close the app after opening a file")
args = parser.parse_args()

app = None
assPath = args.path

if(args.path):
    dirPath = args.path
    imageName = args.asset
else:
    dirPath = None
    imageName = None

def rename(self,main_ui):
    debug.info(dirPath)
    debug.info(imageName)
    format = imageName.split(".")[-1]
    images = glob.glob(dirPath.rstrip(os.sep) + os.sep + "*.%s" %format)
    images.sort()
    debug.info(images)

    newName = str(main_ui.newName.text().strip())
    if newName.endswith("_"):
        pass
    else:
        newName = newName+"_"

    i = 1
    for image in images:
        dst = newName + str("%04d" % i) + "." + format
        src = image
        dst = dirPath+"/"+dst
        print(src)
        print(dst)
        # rename() function will
        # rename all the files
        os.rename(src, dst)
        i += 1

    QApplication.quit()


def mainGui(main_ui):
    main_ui.setWindowTitle(assPath)

    qssFile = os.path.join(projDir, "styleSheet", "stylesheetTest.qss")
    with open(qssFile, "r") as fh:
        main_ui.setStyleSheet(fh.read())

    main_ui.folderName.setText(dirPath+"/")
    main_ui.folderName.setEnabled(False)
    main_ui.oldName.setText(imageName)
    main_ui.oldName.setReadOnly(True)
    main_ui.newName.setToolTip("New Name for the batch of files. Don't put extensions")

    main_ui.renameButton.clicked.connect(lambda self, main_ui = main_ui : rename(self, main_ui))

    main_ui.show()
    main_ui.update()

def mainfunc():
    global app
    app = QApplication(sys.argv)
    main_ui = uic.loadUi(main_ui_file)
    mainGui(main_ui)
    sys.exit(app.exec_())

if __name__ == '__main__':
    setproctitle.setproctitle("BATCH_RENAME")
    mainfunc()

