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
import setproctitle
import subprocess

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

main_ui_file = os.path.join(projDir, "uiFiles", "video_converter.ui")
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
    videoName = args.asset
else:
    dirPath = None
    videoName = None

def convert(self,main_ui):
    debug.info(dirPath)
    debug.info(videoName)
    inputFormat = videoName.split(".")[-1]
    # images = glob.glob(dirPath.rstrip(os.sep) + os.sep + "*.%s" %format)
    # images.sort()
    # debug.info(images)
    oldName = main_ui.input.text().strip()
    input = dirPath+"/"+oldName
    container = main_ui.container.currentText().strip()
    size = main_ui.size.currentText().strip()
    newName = main_ui.output.text().strip()
    if newName:
        pass
    else:
        newName = videoName.split(".")[0]
    output = dirPath+"/"+newName+"."+container

    debug.info(input)
    debug.info(container)
    debug.info(size)
    debug.info(output)

    cmd = None
    ffmpeg = None
    if (os.path.exists("/opt/lib/ffmpeg/bin/ffmpeg")):
        ffmpeg = "/opt/lib/ffmpeg/bin/ffmpeg"
    else:
        debug.info("Not found : /opt/lib/ffmpeg/bin/ffmpeg")
        ffmpeg = "ffmpeg"

    if size == "low":
        cmd = ffmpeg+" -probesize 5000000 -i "+input+" -c:a copy -c:v prores_ks -profile:v 3 -vendor ap10 -pix_fmt yuv422p10le -qscale:v 10 -y "+output
    if size == "same":
        if inputFormat == "mov" and container == "mp4":
            cmd = ffmpeg+" -probesize 5000000 -i "+input+" -c:a copy -c:v prores_ks -profile:v 3 -vendor ap10 -pix_fmt yuv422p10le -qscale:v 10 -y "+output
        else:
            cmd = ffmpeg+" -i "+input+" -c:a copy -c:v copy -y "+output
        # # cmd = ffmpeg+" -i "+input+" -vcodec copy -acodec copy -y "+output
        #     cmd = ffmpeg+" -i "+input+" -pre medium -movflags +faststart -c:a copy -y "+output
        # else:
        # cmd = ffmpeg+" -i "+input+" -c:a copy -c:v copy -y "+output
        # cmd = ffmpeg+" -i "+input+" -c:a copy -c:v copy -q:v 0 -y "+output

    # if size == "same":
    #     cmd = 	ffmpeg+" -i "+input+" -vcodec copy -acodec copy -f "+container+" "+output #same resolution
    # elif size == "low":
    #     cmd = ffmpeg+" -i "+input+" -vcodec libx265 -crf 20 -f "+container+" "+output  # same resolution low size
    debug.info(cmd)
    if cmd:
        try:
            p = subprocess.Popen(cmd, shell=True)
            # p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p.wait()
            if p.wait() != 0:
                raise ValueError("ffmpeg failed")
            else:
                debug.info("done")
                messageBox("Conversion Complete", icon=os.path.join(projDir, "imageFiles", "info-icon-1.png"))
                QApplication.quit()

        except:
            debug.info(str(sys.exc_info()))
            messageBox("Conversion Failed", icon=os.path.join(projDir, "imageFiles", "error-icon-1.png"))
            QApplication.quit()


def messageBox(msg1, msg2="", icon=""):
    msg = QtWidgets.QMessageBox()
    msg.setWindowTitle("Message")
    msg.setText(msg1+"\n"+msg2)
    okBut = msg.addButton("OK", QtWidgets.QMessageBox.NoRole)
    msg.setDefaultButton(okBut)
    if icon:
        msg.setIconPixmap(QtGui.QPixmap(icon))
    else:
        msg.setIcon(QtWidgets.QMessageBox.Information)
    qssFile = os.path.join(projDir, "styleSheet", "stylesheetTest.qss")
    with open(qssFile, "r") as sty:
        msg.setStyleSheet(sty.read())
    msg.exec_()



def mainGui(main_ui):
    main_ui.setWindowTitle(assPath)

    qssFile = os.path.join(projDir, "styleSheet", "stylesheetTest.qss")
    with open(qssFile, "r") as fh:
        main_ui.setStyleSheet(fh.read())

    main_ui.folderName.setText(dirPath+"/")
    main_ui.folderName.setEnabled(False)
    main_ui.input.setText(videoName)
    main_ui.input.setReadOnly(True)
    main_ui.output.setToolTip("New Name for the file. Don't put extensions")

    main_ui.convertButton.clicked.connect(lambda self, main_ui = main_ui : convert(self, main_ui))

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


