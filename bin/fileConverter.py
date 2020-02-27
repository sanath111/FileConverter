#!/usr/bin/python2
# *-* coding: utf-8 *-*
__author__ = "Sanath Shetty K"
__license__ = "GPL"
__email__ = "sanathshetty111@gmail.com"

import os
import sys
# import subprocess
# import tempfile

# tempDir = tempfile.gettempdir()

projDir = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-2])
sys.path.append(projDir)

srcDir = os.path.join(projDir,"src")
sys.path.append(srcDir)

import debug
# debug.info(tempDir)

# projDir = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-2])
# sys.path.append(projDir)

cmd = "python " + srcDir + os.sep +"file_converter.py"
debug.info(cmd)
os.system(cmd)
# with open(tempDir+"/fileConverterLog.txt", "w") as output:
#     subprocess.call(["python", srcDir+"/file_converter.py"], stderr=output)
