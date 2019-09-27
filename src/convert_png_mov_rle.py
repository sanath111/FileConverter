#!/usr/bin/env python2
#-*- coding: utf-8 -*-
__author__ = "Shrinidhi Rao"
__license__ = "GPL"
__email__ = "shrinidhi666@gmail.com"

import sys
import os

projDir = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-2])
sys.path.append(projDir)

import multiprocessing
import glob
import subprocess
import uuid
import shutil


path = os.path.abspath(sys.argv[1])

# cpus = multiprocessing.cpu_count()
pngs = glob.glob(path.rstrip(os.sep) + os.sep + "*.png")
pngs.sort()
mov = "_".join(pngs[-1].split(".")[0].split("_")[:-1]) + ".mov"
png = "_".join(pngs[-1].split(".")[0].split("_")[:-1]) + "_%04d.png"
startFrame = pngs[0].split("_")[-1].rstrip(".png")
endFrame = pngs[-1].split("_")[-1].rstrip(".png")
inputFileFmt = "_".join(pngs[-1].split(".")[0].split("_")[:-1]) + "_"+ startFrame +"-"+ endFrame +".png"

ffmpeg = None
if(os.path.exists("/opt/lib/ffmpeg/bin/ffmpeg")):
  ffmpeg = "/opt/lib/ffmpeg/bin/ffmpeg"
else:
  print("Not found : /opt/lib/ffmpeg/bin/ffmpeg")
  ffmpeg = "ffmpeg"

cmd = ffmpeg +" -probesize 50000000 -apply_trc iec61966_2_1 -r 24 -start_number "+ str(startFrame) +" -i "+ png +" -c:v qtrle -pix_fmt rgb24 -qscale:v 1 -y "+ mov
#iec61966_2_1
# cmd = "djv_convert "+ inputFileFmt +" "+ mov +" -pixel \"RGB F16\" -default_speed 24 -render_filter_high"
p = subprocess.Popen(cmd,shell=True)
p.wait()

