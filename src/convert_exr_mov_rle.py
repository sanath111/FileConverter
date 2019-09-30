#!/usr/bin/env python2
#-*- coding: utf-8 -*-
__author__ = "Shrinidhi Rao"
__license__ = "GPL"
__email__ = "shrinidhi666@gmail.com"

import sys
import os

# sys.path.append(os.sep.join(os.path.abspath(__file__).split(os.sep)[:-2]))
projDir = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-2])
sys.path.append(projDir)

import glob
import subprocess


path = os.path.abspath(sys.argv[1])
# move_path = None
try:
  mov_path = os.path.abspath(sys.argv[2])
except:
  mov_path = None

# cpus = multiprocessing.cpu_count()
exrs = glob.glob(path.rstrip(os.sep) + os.sep + "*.exr")
exrs.sort()
mov = "_".join(exrs[-1].split(".")[0].split("_")[:-1]) + ".mov"
exr = "_".join(exrs[-1].split(".")[0].split("_")[:-1]) + "_%04d.exr"
startFrame = exrs[0].split("_")[-1].rstrip(".exr")
# endFrame = exrs[-1].split("_")[-1].rstrip(".exr")
# inputFileFmt = "_".join(exrs[-1].split(".")[0].split("_")[:-1]) + "_"+ startFrame +"-"+ endFrame +".exr"

# print (exrs)
# print (mov)
# print(exr)
# print (startFrame)
# print (endFrame)
# print (inputFileFmt)

ffmpeg = None
if(os.path.exists("/opt/lib/ffmpeg/bin/ffmpeg")):
  ffmpeg = "/opt/lib/ffmpeg/bin/ffmpeg"
else:
  print("Not found : /opt/lib/ffmpeg/bin/ffmpeg")
  ffmpeg = "ffmpeg"

cmd = ffmpeg +" -probesize 50000000 -apply_trc iec61966_2_1 -r 24 -start_number "+ str(startFrame) +" -i "+ exr +" -c:v qtrle -pix_fmt rgb24 -qscale:v 1 -y "+ mov
# cmd = ffmpeg +" -probesize 50000000 -apply_trc iec61966_2_1 -r 24 -start_number "+ str(startFrame) +" -i "+ exr +" -vframes 100 -c:v qtrle -pix_fmt argb -qscale:v 1 -y "+ mov
# cmd = ffmpeg +" -probesize 50000000 -apply_trc iec61966_2_1 -r 24 -start_number "+ str(startFrame) +" -i "+ exr +" -pix_fmt argb -qscale:v 1 -y "+ mp4
# ffmpeg -apply_trc iec61966_2_1 -start_frame 1100 -i input.$04d.exr output.mp4

#iec61966_2_1
# cmd = "djv_convert "+ inputFileFmt +" "+ mov +" -pixel \"RGB F16\" -default_speed 24 -render_filter_high"
p = subprocess.Popen(cmd,shell=True)
p.wait()

if(mov_path):
  cpCmd = "cp -v "+ mov +" "+ mov_path +"/"
  os.system(cpCmd.rstrip())
else:
  print("Nothing to move after convert")

