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
import subprocess
import pyperclip
import time
import threading

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

srcDir = os.path.join(projDir,"src")
toolsDir = os.path.join(projDir, "tools")
debug.info(toolsDir)

if os.path.exists(toolsDir+os.sep+"ffmpeg"):
    debug.info("ffmpeg exists")
else:
    os.system("cd "+toolsDir+"; unzip "+toolsDir+os.sep+"ffmpeg.zip; cd -")

main_ui_file = os.path.join(projDir, "uiFiles", "file_converter.ui")
debug.info(main_ui_file)

imageFormats = ['png','exr','PNG','EXR','jpg','JPEG']
videoFormats = ['mov','mp4','MP4','avi','mkv']
detectedFormats = []
frameNums = []
missingFrames = []

parser = argparse.ArgumentParser(description="File conversion utility")
# parser.add_argument("-a","--asset",dest="asset",help="colon separated Asset path")
parser.add_argument("-p","--path",dest="path",help="Absolute path of the folder containing image sequence or videos")
# parser.add_argument("-c","--close",dest="close",action="store_true",help="Close the app after opening a file")
args = parser.parse_args()



app = None
assPath = args.path
# assDets = rbhus.utilsPipe.getAssDetails(assPath=assPath)
# ROOTDIR_ASSET = rbhus.utilsPipe.getAbsPath(assPath)
if(args.path):
    ROOTDIR = args.path
else:
    ROOTDIR = "/tmp/"
  # print("provide a path")
  # ROOTDIR = ROOTDIR_ASSET


CUR_DIR_SELECTED = None


class FSM4Files(QFileSystemModel):

    def __init__(self,**kwargs):
        super(FSM4Files, self).__init__(**kwargs)


class FSM(QFileSystemModel):

    def __init__(self,**kwargs):
      super(FSM, self).__init__(**kwargs)


# class CustomMessageBox(QtWidgets.QMessageBox):
#
#     def __init__(self, *__args):
#         QtWidgets.QMessageBox.__init__(self)
#         self.timeout = 0
#         self.autoclose = False
#         self.currentTime = 0
#         # qssFile = os.path.join(projDir, "styleSheet", "stylesheetTest.qss")
#         # with open(qssFile, "r") as sty:
#         #     self.setStyleSheet(sty.read())
#
#     def showEvent(self, QShowEvent):
#         self.currentTime = 0
#         if self.autoclose:
#             self.startTimer(1000)
#
#     def timerEvent(self, *args, **kwargs):
#         self.currentTime += 1
#         if self.currentTime >= self.timeout:
#             debug.info("done")
#             self.done(0)
#
#     @staticmethod
#     def showWithTimeout(timeoutSeconds, message, title, icon=QtWidgets.QMessageBox.Information, buttons=QtWidgets.QMessageBox.Ok):
#         w = CustomMessageBox()
#         w.autoclose = True
#         w.timeout = timeoutSeconds
#         w.setText(message)
#         w.setWindowTitle(title)
#         w.setIcon(icon)
#         w.setStandardButtons(buttons)
#         w.exec_()


def dirSelected(idx, modelDirs, main_ui):
    global CUR_DIR_SELECTED

    pathSelected = modelDirs.filePath(idx)
    # main_ui.labelFile.setText(str(pathSelected).replace(ROOTDIR,"-"))
    CUR_DIR_SELECTED = pathSelected.strip()
    debug.info(CUR_DIR_SELECTED)

    main_ui.currentFolder.clear()
    main_ui.currentFolder.setText(CUR_DIR_SELECTED)

    modelFiles = FSM4Files(parent=main_ui)

    modelFiles.setRootPath(CUR_DIR_SELECTED)
    modelFiles.setFilter(QtCore.QDir.Files | QtCore.QDir.NoDotAndDotDot)
    rootIdx = modelFiles.index(CUR_DIR_SELECTED)


    main_ui.listFiles.setModel(modelFiles)
    main_ui.listFiles.setRootIndex(rootIdx)

    getDetails(CUR_DIR_SELECTED, main_ui)

    main_ui.messages.setText("Click Convert to start")


def copyPath(self, main_ui):
    path = main_ui.currentFolder.text().strip()
    # main_ui.outputFolder.clear()
    # main_ui.outputFolder.setText(path)
    pyperclip.copy(path)


def pastePath(self, main_ui):
    path = pyperclip.paste()
    debug.info(path)
    main_ui.currentFolder.clear()
    main_ui.currentFolder.setText(path.strip())


def previousDir(self, main_ui):
    # debug.info("previous directory")
    ROOTDIR = main_ui.currentFolder.text().strip()
    ROOTDIRNEW = os.sep.join(ROOTDIR.split(os.sep)[:-1])
    debug.info(ROOTDIRNEW)

    setDir(ROOTDIRNEW, main_ui)


def changeDir(self, main_ui):
    ROOTDIR = main_ui.currentFolder.text().strip()
    ROOTDIRNEW = os.path.abspath(os.path.expanduser(ROOTDIR))
    # home = os.path.expanduser(ROOTDIR)
    # debug.info(home)
    debug.info (ROOTDIRNEW)

    if os.path.exists(ROOTDIRNEW):
        setDir(ROOTDIRNEW, main_ui)
    # CustomMessageBox.showWithTimeout(3, "Auto close in 3 seconds", "QMessageBox with autoclose", icon=QtWidgets.QMessageBox.Warning)


def setDir(ROOTDIRNEW, main_ui):
    modelDirs = FSM()
    modelDirs.setFilter(QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot)
    modelDirs.setRootPath(ROOTDIRNEW)

    main_ui.treeDirs.setModel(modelDirs)

    main_ui.treeDirs.hideColumn(1)
    main_ui.treeDirs.hideColumn(2)
    main_ui.treeDirs.hideColumn(3)

    rootIdx = modelDirs.index(ROOTDIRNEW)
    main_ui.treeDirs.setRootIndex(rootIdx)

    dirSelected(rootIdx, modelDirs, main_ui)


def getDetails(ROOTDIRNEW, main_ui):
    path = os.path.abspath(ROOTDIRNEW)
    global detectedFormats
    global frameNums
    global missingFrames
    del detectedFormats[:]
    del frameNums[:]
    del missingFrames[:]

    for format in imageFormats:
        images = glob.glob(path.rstrip(os.sep) + os.sep + "*.%s" %format)
        images.sort()
        if images:
            debug.info(len(images))
            # frameNums = []
            # if len(images)>1:
            for n in range(0,len(images)):
                frameNum = images[n].split("_")[-1].rstrip(".%s" %format)
                # debug.info(frameNum)
                try:
                    frameNums.append(int(frameNum))
                except:
                    pass
            # del detectedFormats[:]
            frameNums.sort()
            # debug.info(frameNums)

            if frameNums:
                for x in range(frameNums[0], frameNums[-1] + 1):
                    if x not in frameNums:
                        missingFrames.append(x)
                missingFrames.sort()
                debug.info(missingFrames)

            detectedFormats.append(format)
            # if "_" in name:
            startFrame = images[0].split("_")[-1].rstrip(".%s" %format)
            # else:
            #   temp = re.findall(r'\d+', name)
            #   res = list(map(int, temp))
            #   debug.info(res)
            #   startFrame = str(res)
            endFrame = images[-1].split("_")[-1].rstrip(".%s" %format)
            # debug.info(startFrame+endFrame)
            outputFormat = main_ui.outputFormat.currentText().strip()
            mov = "_".join(".".join(images[-1].split(".")[:-1]).split("_")[:-1]) + "." + outputFormat
            main_ui.fileName.clear()
            main_ui.startFrame.clear()
            main_ui.endFrame.clear()
            main_ui.outputFolder.clear()

            main_ui.fileName.setText(mov)
            main_ui.startFrame.setText(startFrame)
            main_ui.endFrame.setText(endFrame)
            main_ui.outputFolder.setText(path)
    # inputFileFmt = "_".join(exrs[-1].split(".")[0].split("_")[:-1]) + "_" + startFrame + "-" + endFrame + ".exr"
    main_ui.inputFormat.clear()
    main_ui.inputFormat.addItems(detectedFormats)


def startConvert(self, main_ui):
    global detectedFormats
    main_ui.progressBar.setValue(0)
    text = main_ui.outputFolder.text().strip()
    if detectedFormats:
        debug.info(detectedFormats)
    if missingFrames:
        missingfrms = ','.join(map(str, missingFrames))
        messageBox("missing frames:",missingfrms,icon=os.path.join(projDir, "imageFiles", "error-icon-1.png"))
    else:
        if text:
            debug.info(text)
            outputDir = os.path.abspath(os.path.expanduser(text))+"/"
            if os.path.exists(outputDir):
                debug.info(outputDir)

                try:
                    startFrame = "%04d" %int(main_ui.startFrame.text().strip())
                    endFrame = "%04d" %int(main_ui.endFrame.text().strip())
                    frames = str((int(endFrame.lstrip("0")) - int(startFrame.lstrip("0"))) + 1)
                    if int(frames)<=0:
                        # messageBox("End frame can't be less than start frame",icon=os.path.join(projDir, "imageFiles", "error-icon-1.png"))
                        raise ValueError("End frame can't be less than start frame")
                    else:
                        outputFile = main_ui.fileName.text().strip()
                        input = None
                        # input = outputFile.split(".")[0] + "_%04d."+inputFormat
                        if detectedFormats:
                            dirPath = os.path.abspath(main_ui.currentFolder.text().strip())
                            debug.info(detectedFormats)
                            format = detectedFormats[0]
                            images = glob.glob(dirPath.rstrip(os.sep) + os.sep + "*.%s" %format)
                            # debug.info(images)
                            input = "_".join(".".join(images[-1].split(".")[:-1]).split("_")[:-1]) + "_%04d."+format
                            debug.info(input)
                            if input == "_%04d."+format:
                                raise ValueError("Invalid File Name")

                        encoding = main_ui.encoding.currentText().strip()
                        colorMode = main_ui.colorMode.currentText().strip()
                        inputFormat = main_ui.inputFormat.currentText().strip()
                        outputFormat = main_ui.outputFormat.currentText().strip()

                        # ffmpeg = None
                        # if (os.path.exists("/opt/lib/ffmpeg/bin/ffmpeg")):
                        #     ffmpeg = "/opt/lib/ffmpeg/bin/ffmpeg"
                        # else:
                        #     debug.info("Not found : /opt/lib/ffmpeg/bin/ffmpeg")
                        #     ffmpeg = "ffmpeg"
                        ffmpeg = ""
                        if os.path.exists(toolsDir + os.sep + "ffmpeg"):
                            ffmpeg = toolsDir + os.sep + "ffmpeg"
                        debug.info(ffmpeg)

                        Encoding = encoding
                        if outputFormat == "mp4":
                            if inputFormat == "exr":
                                Encoding = "h264"
                            else:
                                Encoding = "copy"
                        if outputFormat == "mov":
                            Encoding = encoding
                        #     cmd = ffmpeg +" -probesize 50000000 -apply_trc iec61966_2_1 -r 24 -start_number "+\
                        #           str(startFrame) +" -i "+ input +" -vframes "+frames+" -c:v copy -pix_fmt "+colorMode+" -qscale:v 1 -y "+ outputFile
                        # else:
                        cmd = ffmpeg +" -probesize 50000000 -apply_trc iec61966_2_1 -r 24 -start_number "+\
                              str(startFrame) +" -i "+ input +" -vframes "+frames+" -c:v "+Encoding+" -pix_fmt "+colorMode+" -qscale:v 1 -y "+ outputFile

                        debug.info (cmd)
                        try:
                            main_ui.progressBar.setRange(1, int(frames))

                            thread = pexpect.spawn(cmd)

                            thread.logfile = open("/tmp/fileConverterLog.txt", "w")

                            cpl = thread.compile_pattern_list([pexpect.EOF,"frame= *\d+",'(.+)'])

                            listOfI = []
                            while True:
                                i = thread.expect_list(cpl, timeout=None)

                                if i == 0:  # EOF
                                    debug.info("the sub process exited")
                                    break

                                elif i == 1:
                                    # if i not in listOfI:
                                    listOfI.append(i)
                                    frame_number = thread.match.group(0)
                                    temp = re.findall(r'\d+', frame_number)
                                    res = list(map(int, temp))
                                    debug.info(res[0])

                                    main_ui.messages.hide()
                                    main_ui.progressBar.show()
                                    main_ui.progressBar.setValue(int(res[0]))

                                elif i == 2:
                                    # if i not in listOfI:
                                    listOfI.append(i)
                                    pass

                            debug.info(listOfI)
                            if (all(p == 2 for p in listOfI) and len(listOfI) > 0) == True:
                                raise ValueError("ffmpeg failed")
                            else:
                                cpCmd = "cp -v " + outputFile + " " + outputDir
                                debug.info(cpCmd)
                                os.system(cpCmd.rstrip())
                                main_ui.messages.show()
                                main_ui.messages.setText("Conversion complete")
                                # messageBox("Conversion Complete",icon=os.path.join(projDir, "imageFiles", "info-icon-1.png"))
                            thread.close()
                            main_ui.progressBar.hide()

                        except:
                            debug.info(str(sys.exc_info()[1]))
                            main_ui.messages.show()
                            main_ui.messages.setText("ffmpeg failed")
                            # messageBox(str(sys.exc_info()[1]),icon=os.path.join(projDir, "imageFiles", "coming-soon-icon-1.png"))
                except:
                    err = str(sys.exc_info()[1])
                    debug.info(err)
                    if "invalid literal for int()" in err:
                        main_ui.messages.setText("Error! Check start and end frames")
                    if "End frame can't be less than start frame" in err:
                        main_ui.messages.setText("Error! Check start and end frames")
                    if "Invalid File Name" in err:
                        main_ui.messages.setText("Invalid File Name, Try Renaming")
                    # messageBox(str(sys.exc_info()[1]),icon=os.path.join(projDir, "imageFiles", "error-icon-1.png"))
            else:
                main_ui.messages.setText("Output folder doesn't exist")
                # messageBox("No such Path",icon=os.path.join(projDir, "imageFiles", "error-icon-1.png"))
        else:
            main_ui.messages.setText("Specify output folder")
            # messageBox("Specify Output Directory",icon=os.path.join(projDir, "imageFiles", "error-icon-1.png"))


def changeFormat(self, main_ui):
    format = main_ui.outputFormat.currentText().strip()
    # filename = main_ui.fileName.text().strip().split(".")[0] + "."+format
    filename = ".".join(main_ui.fileName.text().strip().split(".")[:-1]) + "." + format
    main_ui.fileName.clear()
    main_ui.fileName.setText(filename)


def getSelectedFiles(main_ui):
    files =[]
    selectedItems = main_ui.listFiles.selectedIndexes()
    for selectedItem in selectedItems:
        files.append(selectedItem.data())

    return(files)


def openFile(self, main_ui):
    debug.info("double clicked!!!")
    selectedFiles = getSelectedFiles(main_ui)
    path = os.path.abspath(main_ui.currentFolder.text().strip())
    selectedFilePath = path+os.sep+selectedFiles[0]

    formatOfSelected = selectedFiles[0].split(".")[-1]
    debug.info(formatOfSelected)
    openCmd = " "
    if formatOfSelected in imageFormats:
        openCmd = "gwenview " + selectedFilePath
    if formatOfSelected in videoFormats:
        openCmd = "mpv " + selectedFilePath
    # openCmd = "xdg-open "+selectedFilePath
    debug.info(openCmd)
    subprocess.Popen(openCmd, shell=True)


def popUpFiles(main_ui,context,pos):
    menu = QtWidgets.QMenu()
    renameAction = menu.addAction("Batch Rename")
    convertAction = menu.addAction("Convert Video")

    selectedFiles = getSelectedFiles(main_ui)
    debug.info(selectedFiles)
    action = menu.exec_(context.mapToGlobal(pos))
    path = os.path.abspath(main_ui.currentFolder.text().strip())
    # filePath = path+"/"+selectedFiles[0]
    # debug.info(filePath)
    if selectedFiles:
        formatOfSelected = selectedFiles[0].split(".")[-1]
        debug.info(formatOfSelected)

        if formatOfSelected in imageFormats:
            if action == renameAction:
                debug.info("rename action")
                cmd = "python "+os.path.join(projDir, "src", "batch_rename.py")+" --path "+path+" --asset "+selectedFiles[0]
                debug.info(cmd)
                p = subprocess.Popen(cmd, shell=True)
                # p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                p.wait()

        if formatOfSelected in videoFormats:
            if action == convertAction:
                debug.info("convert action")
                cmd = "python "+os.path.join(projDir, "src", "video_converter.py")+" --path "+path+" --asset "+selectedFiles[0]
                debug.info(cmd)
                p = subprocess.Popen(cmd, shell=True)
                # p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                p.wait()


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

    main_ui.currentFolder.clear()
    main_ui.currentFolder.setText(ROOTDIR)

    ROOTDIRNEW = os.path.abspath(main_ui.currentFolder.text().strip())
    debug.info(ROOTDIRNEW)

    modelDirs = FSM()
    modelDirs.setFilter( QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot)
    modelDirs.setRootPath(ROOTDIRNEW)

    main_ui.treeDirs.setModel(modelDirs)

    main_ui.treeDirs.hideColumn(1)
    main_ui.treeDirs.hideColumn(2)
    main_ui.treeDirs.hideColumn(3)
    main_ui.treeDirs.setHeaderHidden(True)

    rootIdx = modelDirs.index(ROOTDIRNEW)
    main_ui.treeDirs.setRootIndex(rootIdx)

    prevDirIcon = QtGui.QPixmap(os.path.join(projDir, "imageFiles", "arrow-up-1.png"))
    goIcon = QtGui.QPixmap(os.path.join(projDir, "imageFiles", "arrow-right-1.png"))
    copyIcon = QtGui.QPixmap(os.path.join(projDir, "imageFiles", "copy-icon-1.png"))
    pasteIcon = QtGui.QPixmap(os.path.join(projDir, "imageFiles", "paste-icon-1.png"))

    main_ui.copyButton.setIcon(QtGui.QIcon(copyIcon))
    main_ui.pasteButton.setIcon(QtGui.QIcon(pasteIcon))
    main_ui.upButton.setIcon(QtGui.QIcon(prevDirIcon))
    main_ui.goButton.setIcon(QtGui.QIcon(goIcon))

    main_ui.copyButton.setToolTip("Copy to Clipboard")
    main_ui.pasteButton.setToolTip("Paste from Clipboard")
    main_ui.upButton.setToolTip("Previous Folder")
    main_ui.goButton.setToolTip("Go to Folder")


    main_ui.treeDirs.clicked.connect(lambda idnx, modelDirs=modelDirs, main_ui = main_ui : dirSelected(idnx, modelDirs, main_ui))
    main_ui.copyButton.clicked.connect(lambda self, main_ui = main_ui : copyPath(self, main_ui))
    main_ui.pasteButton.clicked.connect(lambda self, main_ui = main_ui : pastePath(self, main_ui))
    main_ui.goButton.clicked.connect(lambda self, main_ui = main_ui : changeDir(self, main_ui))
    main_ui.upButton.clicked.connect(lambda self, main_ui = main_ui : previousDir(self, main_ui))
    main_ui.convertButton.clicked.connect(lambda self, main_ui = main_ui : startConvert(self, main_ui))
    main_ui.outputFormat.currentIndexChanged.connect(lambda self, main_ui=main_ui: changeFormat(self, main_ui))


    main_ui.listFiles.customContextMenuRequested.connect(lambda pos, context = main_ui.listFiles.viewport(), main_ui = main_ui: popUpFiles(main_ui, context, pos))
    main_ui.listFiles.doubleClicked.connect(lambda self, main_ui = main_ui : openFile(self, main_ui))

    main_ui.progressBar.hide()
    main_ui.messages.setText("Click Convert to start")

    main_ui.show()
    main_ui.update()


    qtRectangle = main_ui.frameGeometry()
    centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center()
    qtRectangle.moveCenter(centerPoint)
    main_ui.move(qtRectangle.topLeft())


def mainfunc():
    global app
    app = QApplication(sys.argv)
    main_ui = uic.loadUi(main_ui_file)
    mainGui(main_ui)
    # ex = App()
    sys.exit(app.exec_())


if __name__ == '__main__':
    setproctitle.setproctitle("FILE_CONVERTER")
    mainfunc()

