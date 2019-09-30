#!/usr/bin/python2
# *-* coding: utf-8 *-*
__author__ = "Sanath Shetty K"
__license__ = "GPL"
__email__ = "sanathshetty111@gmail.com"


import debug
import argparse
import glob
import multiprocessing
import os
import subprocess
import sys
import time
import uuid
try:
  import arrow
except:
  pass
import setproctitle
import simplejson
import zmq
import re
import shutil
import hashlib
import tempfile
import shlex
import resource
import timeit
import pexpect

from PyQt5.QtWidgets import QApplication, QFileSystemModel, QListWidgetItem
from PyQt5 import QtCore, uic, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

projDir = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-2])
sys.path.append(projDir)

main_ui_file = os.path.join(projDir, "uiFiles", "file_converter.ui")
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



  # def data(self, index, role):
  #   if (index.isValid()):
  #     if(index.column() == 0):
  #       if( role == QtCore.Qt.DecorationRole):
  #         filePath = os.path.abspath(str(self.filePath(index)))
  #         pathSelected = os.path.relpath(os.path.dirname(filePath), ROOTDIR)
  #         fName = os.path.basename(filePath)
  #         # fThumbz = os.path.join(thumbsDbDir, pathSelected, fName + ".png")
  #         # if (os.path.exists(fThumbz)):
  #           # rbhus.debug.info(fThumbz)
  #           # pixmap = QtGui.QPixmap(fThumbz)
  #           return pixmap.scaled(64, 64, QtCore.Qt.KeepAspectRatio)
  #
  #   return super(FSM4Files, self).data(index, role)


class FSM(QFileSystemModel):

  def __init__(self,**kwargs):
    super(FSM, self).__init__(**kwargs)
    # self.fileDets = None

def dirSelected(idx, modelDirs, main_ui):
  global CUR_DIR_SELECTED

  pathSelected = modelDirs.filePath(idx)
  # main_ui.labelFile.setText(str(pathSelected).replace(ROOTDIR,"-"))
  CUR_DIR_SELECTED = pathSelected.strip()
  debug.info(CUR_DIR_SELECTED)

  main_ui.currentFolder.setText(CUR_DIR_SELECTED)

  modelFiles = FSM4Files(parent=main_ui)

  modelFiles.setRootPath(CUR_DIR_SELECTED)
  modelFiles.setFilter(QtCore.QDir.Files | QtCore.QDir.NoDotAndDotDot)
  rootIdx = modelFiles.index(CUR_DIR_SELECTED)


  main_ui.listFiles.setModel(modelFiles)
  main_ui.listFiles.setRootIndex(rootIdx)

  getDetails(CUR_DIR_SELECTED, main_ui)



# def getSelectedFiles(main_ui):
#   files =[]
#   if(main_ui.checkDetails.isChecked()):
#     selectedIdxs = main_ui.tableFiles.selectionModel().selectedRows()
#     modelFiles = main_ui.tableFiles.model()
#     for selectedIdx in selectedIdxs:
#       files.append(modelFiles.filePath(selectedIdx))
#   else:
#     selectedItems = main_ui.listFiles.selectedItems()
#     for selectedItem in selectedItems:
#       files.append(selectedItem.media.absPath)
#
#
#   return(files)

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
  setDir(ROOTDIRNEW, main_ui)

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
  # debug.info(path)
    # move_path = None
    # try:
    #     mov_path = os.path.abspath(sys.argv[2])
    # except:
    #     mov_path = None

    # cpus = multiprocessing.cpu_count()
  # onlyfiles = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
  # debug.info(onlyfiles)
  # for file in onlyfiles:
  detectedFormats = []
  for format in imageFormats:
    images = glob.glob(path.rstrip(os.sep) + os.sep + "*.%s" %format)
    images.sort()
    if images:
      detectedFormats.append(format)
      # debug.info(images)
  # mov = "_".join(exrs[-1].split(".")[0].split("_")[:-1]) + ".mov"
  # exr = "_".join(exrs[-1].split(".")[0].split("_")[:-1]) + "_%04d.exr"
  #     name = images[0]
  #     debug.info(name)
      # try:
      #   key, value = name.split("_")
      # except ValueError:
      #   debug.info("Failure")
      # else:
      #   debug.info(key+value)
      # if "_" in name:
      startFrame = images[0].split("_")[-1].rstrip(".%s" %format)
      # else:
      #   temp = re.findall(r'\d+', name)
      #   res = list(map(int, temp))
      #   debug.info(res)
      #   startFrame = str(res)
      endFrame = images[-1].split("_")[-1].rstrip(".%s" %format)
      # debug.info(startFrame+endFrame)
      mov = "_".join(images[-1].split(".")[0].split("_")[:-1]) + ".mov"

      main_ui.fileName.setText(mov)
      main_ui.startFrame.setText(startFrame)
      main_ui.endFrame.setText(endFrame)
  # inputFileFmt = "_".join(exrs[-1].split(".")[0].split("_")[:-1]) + "_" + startFrame + "-" + endFrame + ".exr"
  main_ui.inputFormat.clear()
  main_ui.inputFormat.addItems(detectedFormats)


def startConvert(self, main_ui):
  main_ui.progressBar.setValue(0)
  text = main_ui.outputFolder.text().strip()
  if text:
    debug.info(text)
    outputDir = os.path.abspath(os.path.expanduser(text))+"/"
    if os.path.exists(outputDir):
      debug.info(outputDir)

      startFrame = "%04d" %int(main_ui.startFrame.text().strip())
      endFrame = main_ui.endFrame.text().strip()
      frames = str((int(endFrame.lstrip("0")) - int(startFrame.lstrip("0"))) + 1)
      # debug.info(startFrame)
      # debug.info(frames)
      outputFile = main_ui.fileName.text().strip()
      inputFormat = main_ui.inputFormat.currentText().strip()
      input = outputFile.split(".")[0] + "_%04d."+inputFormat
      # debug.info (input)
      encoding = main_ui.encoding.currentText().strip()
      colorMode = main_ui.colorMode.currentText().strip()
      outputFormat = main_ui.outputFormat.currentText().strip()

      ffmpeg = None
      if (os.path.exists("/opt/lib/ffmpeg/bin/ffmpeg")):
          ffmpeg = "/opt/lib/ffmpeg/bin/ffmpeg"
      else:
          debug.info("Not found : /opt/lib/ffmpeg/bin/ffmpeg")
          ffmpeg = "ffmpeg"

      if outputFormat == "mp4":
        cmd = ffmpeg +" -probesize 50000000 -apply_trc iec61966_2_1 -r 24 -start_number "+ str(startFrame) +" -i "+ input +" -vframes "+frames+" -pix_fmt "+colorMode+" -qscale:v 1 -y "+ outputFile
      else:
        cmd = ffmpeg +" -probesize 50000000 -apply_trc iec61966_2_1 -r 24 -start_number "+ str(startFrame) +" -i "+ input +" -vframes "+frames+" -c:v "+encoding+" -pix_fmt "+colorMode+" -qscale:v 1 -y "+ outputFile

      debug.info (cmd)
      try:
          # run_command(cmd)
          # times = {}
          # startTime = int(round(time.time() * 1000))
          # times["st"] = startTime
          # p = subprocess.Popen(cmd, shell=True)
          # # p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
          # # out, err = p.communicate()
          # # debug.info(err)
          # # p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
          # # p = subprocess.Popen(shlex.split(cmd), stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
          # # ffmpeg_output, _ = p.communicate()
          # # print(ffmpeg_output)
          # # p.wait()
          # main_ui.progressBar.setRange(int(startFrame.lstrip("0")), int(endFrame.lstrip("0")))
          # count = 0
          # while count < int(endFrame.lstrip("0")):
          #   # debug.info(count)
          #   count += 1
          #   time.sleep(0.04)
          #   main_ui.progressBar.setValue(count)
          #
          # p.wait()
          # poll = p.poll()
          # if poll == None:
          #   debug.info("alive")
          #
          # else:
          #   debug.info("dead")
          # endTime = int(round(time.time() * 1000))
          # times["et"] = endTime
          # info = resource.getrusage(resource.RUSAGE_CHILDREN)
          # debug.info(info)
          main_ui.progressBar.setRange(int(startFrame.lstrip("0")), int(endFrame.lstrip("0")))

          thread = pexpect.spawn(cmd)
          # print "started %s" % cmd
          # if "Conversion failed!" in thread.read():
          #     debug.info("error!!!")
          # debug.info(thread.before)
          cpl = thread.compile_pattern_list([
              pexpect.EOF,
              "frame= *\d+",
              '(.+)'
          ])
          # if thread.expect("Conversion failed!"):
          #     debug.info("error!!!")
          listOfI = []
          while True:
              i = thread.expect_list(cpl, timeout=None)
              if i == 0:  # EOF
                  debug.info("the sub process exited")
                  # cpCmd = "cp -v " + outputFile + " " + outputDir
                  # os.system(cpCmd.rstrip())
                  # messageBox("Conversion Complete",icon=os.path.join(projDir, "imageFiles", "info-icon-1.png"))
                  break

              elif i == 1:
                  # if i not in listOfI:
                  listOfI.append(i)
                  frame_number = thread.match.group(0)
                  # debug.info(frame_number)
                  temp = re.findall(r'\d+', frame_number)
                  res = list(map(int, temp))
                  debug.info(res[0])
                  # main_ui.progressBar.setRange(int(startFrame.lstrip("0")), int(endFrame.lstrip("0")))
                  # count = 0
                  # while count < int(endFrame.lstrip("0")):
                  #   # debug.info(count)
                  #   count += 1
                  #   time.sleep(0.04)
                  main_ui.progressBar.setValue(int(res[0]))

              elif i == 2:
                  # if i not in listOfI:
                  listOfI.append(i)
                  # debug.info("error!!!")
                  # raise ValueError("Not Available yet")
                  # break
                  # unknown_line = thread.match.group(0)
                  # print unknown_line
                  pass
          debug.info(listOfI)
          if (all(p == 2 for p in listOfI) and len(listOfI) > 0) == True:
              raise ValueError("Not available yet")
          # debug.info(all(p == 2 for p in listOfI) and len(listOfI) > 0)
          else:
              cpCmd = "cp -v " + outputFile + " " + outputDir
              os.system(cpCmd.rstrip())
              messageBox("Conversion Complete",icon=os.path.join(projDir, "imageFiles", "info-icon-1.png"))
          thread.close()

          #
          # if p.returncode != 0:
          #     raise NameError
          # else:
          #     # debug.info(times)
          #     # tt = times["et"] - times["st"]
          #     # debug.info(tt)
          #     # if tt>0:
          #     #   main_ui.progressBar.setValue(100)
          #
          #     # cmdThread = TaskThread(str(cmd))
          #     # i = cmdThread.notifyProgress
          #     # debug.info(i)
          #     # cmdThread.notifyProgress.connect(lambda self, i = i, main_ui = main_ui : progress(self, i, main_ui))
          #     # cmdThread.start()
          #     cpCmd = "cp -v " + outputFile + " " + outputDir
          #     os.system(cpCmd.rstrip())
          #     messageBox("Conversion Complete",icon=os.path.join(projDir, "imageFiles", "info-icon-1.png"))

      except:
          debug.info(str(sys.exc_info()))
          messageBox("Failed, Feature coming soon",icon=os.path.join(projDir, "imageFiles", "coming-soon-icon-1.png"))
    else:
      messageBox("No such Path",icon=os.path.join(projDir, "imageFiles", "error-icon-1.png"))
  else:
    messageBox("Specify Output Directory",icon=os.path.join(projDir, "imageFiles", "error-icon-1.png"))


# def run_command(command):
#   process = subprocess.Popen(shlex.split(command), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#   while True:
#     output = process.stdout.readline()
#     if output == '' and process.poll() is not None:
#         break
#     if output:
#         debug.info(output.strip())
#   rc = process.poll()
#   debug.info(rc)



# def progress(self, i, main_ui):
#   main_ui.progressBar.setValue(i)
#
#
# class TaskThread(QtCore.QThread):
#   notifyProgress = QtCore.pyqtSignal(int)
#   def __init__(self, cmd):
#     super(TaskThread, self).__init__(cmd)
#     self.cmd = cmd
#   def run(self):
#     p = subprocess.Popen(self.cmd, shell=True)
#     p.wait()
#     if p.returncode != 0:
#       self.notifyProgress.emit(0)
#     else:
#       self.notifyProgress.emit(100)



def changeFormat(self, main_ui):
  format = main_ui.outputFormat.currentText().strip()
  filename = main_ui.fileName.text().strip().split(".")[0] + "."+format
  main_ui.fileName.setText(filename)


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

  rootIdx = modelDirs.index(ROOTDIRNEW)
  main_ui.treeDirs.setRootIndex(rootIdx)

  prevDirIcon = QtGui.QPixmap(os.path.join(projDir, "imageFiles", "arrow-up-1.png"))
  goIcon = QtGui.QPixmap(os.path.join(projDir, "imageFiles", "arrow-right-1.png"))

  main_ui.upButton.setIcon(QtGui.QIcon(prevDirIcon))
  main_ui.goButton.setIcon(QtGui.QIcon(goIcon))

  # main_ui.progressBar.setRange(0,100)

  main_ui.treeDirs.clicked.connect(lambda idnx, modelDirs=modelDirs, main_ui = main_ui : dirSelected(idnx, modelDirs, main_ui))
  main_ui.goButton.clicked.connect(lambda self, main_ui = main_ui : changeDir(self, main_ui))
  main_ui.upButton.clicked.connect(lambda self, main_ui = main_ui : previousDir(self, main_ui))
  main_ui.convertButton.clicked.connect(lambda self, main_ui = main_ui : startConvert(self, main_ui))
  main_ui.outputFormat.currentIndexChanged.connect(lambda self, main_ui=main_ui: changeFormat(self, main_ui))

  # main_ui.listFiles.clicked.connect(lambda idnx, main_ui = main_ui :filesSelected(modelFiles,main_ui))
  #
  # main_ui.listFiles.customContextMenuRequested.connect(lambda pos, context = main_ui.listFiles, main_ui = main_ui: popUpFiles(main_ui, context, pos))
  # main_ui.tableFiles.customContextMenuRequested.connect(lambda pos, context = main_ui.tableFiles, main_ui = main_ui: popUpFiles(main_ui, context, pos))
  # main_ui.treeDirs.customContextMenuRequested.connect(lambda pos, main_ui = main_ui: popUpFolders(main_ui, pos))

  # main_ui.checkDetails.clicked.connect(lambda click, main_ui=main_ui: toggleView(main_ui))
  # main_ui.checkDetails.setChecked(True)
  # toggleView(main_ui)

  main_ui.show()
  main_ui.update()
  # dirSelected(curRootIdx, modelDirs, main_ui)

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
