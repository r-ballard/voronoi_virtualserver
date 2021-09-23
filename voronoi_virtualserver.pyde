import sys
sys.path.append(PYTHON 2 VIRTUAL ENVIRONMENT SITE PACKAGES PATH)
import requests
import configparser
import os
import random
add_library('VideoExport')
add_library('minim')



config = configparser.ConfigParser()
config.readfp(open(CONFIG FILE DIRECTORY PATH))

base_url = config.get('meta','base_url')

song_title = config.get('meta','song_title')
song_dir = config.get('paths','song_dir')
song_path = os.path.join(song_dir,song_title)

videoexport = VideoExport
minim = Minim
fft = FFT

#separator for input text file
sep = '|'
#set frames per second to be rendered
movieFPS = 30
frame_duration = 1

reader = None

n_points = 500

sizeH = 800
sizeW = 600

screen_corner_points = [[0,0],[sizeW,0],[0,sizeH],[sizeW,sizeH]]
mask_polygon = [[5, 5], [sizeW - 5, 5],
                    [sizeW - 5, sizeH - 5], [5, sizeH - 5]]


points = []
points = requests.post(base_url + "/RandomPointsInsidePolygon", json={"polygon": mask_polygon,
                                                                    "n": n_points}).json()

#TODO modify this to take 5 frame rolling average or something similar
#Variables which define the "zones" of the spectrum
#For example, for bass, we only take the first 33% of the total spectrum
specLow = 0.03
specMid = 0.125
specHi = 0.20

#Score values ​​for each zone
scoreLow = 0
scoreMid = 0
scoreHi = 0

#Previous value, to soften the reduction
oldScoreLow = scoreLow
oldScoreMid = scoreMid
oldScoreHi = scoreHi

#Softening value
scoreDecreaseRate = 25

#Creating window arrays
scoreLowWindow = []
scoreMidWindow = []
scoreHiWindow = []



test_url_string = "test"

line_no = 0

def setup():
    global screen_corner_points, base_url, reader, videoExport, mask_polygon, n_points

    size(sizeW, sizeH)
    noFill()
    smooth()

    reader = open(song_path + ".txt", 'r')

    #https://discourse.processing.org/t/outputting-video-gif/11301

    videoExport = VideoExport(this)
    videoExport.setFrameRate(movieFPS)
    videoExport.setAudioFileName(song_path)
    videoExport.startMovie()

def draw():
    global oldScoreLow, oldScoreMid, oldScoreHi, scoreLow, scoreMid, scoreHi, specLow, specMid, specHi, screen_corner_points, base_url, reader, videoExport, mask_polygon, points
    noFill()
    background(0)
    stroke(235, 64, 52)
    
    line_str = ''
    line_list = []

    try:
        line_str = reader.next().rstrip('\n')
    except StopIteration, si:
        print("File Done.")

    if line_str:
        line_list = line_str.split("|")
        sound_time = float(line_list[0])
    else:
        videoExport.endMovie()
        exit()



    '''if not line_str:
        videoExport.endMovie()
        exit()
    else:
        line_list = line_str.split("|")
        sound_time = float(line_list[0])'''
                        
      #Calculation of the "scores" (power) for three categories of sound
      #First, save the old values

    while (videoExport.getCurrentTime() < sound_time + frame_duration * 0.5):
        oldScoreLow = scoreLow
        oldScoreMid = scoreMid
        oldScoreHi = scoreHi
    
        scoreLow = 0
        scoreMid = 0
        scoreHi = 0
    
        for i in range(1,len(line_list)):
            temp_val = float(line_list[i])
            
            if i <= float(len(line_list)*specLow):
                scoreLow += temp_val
            elif i <= float(len(line_list)*specMid):
                scoreMid += temp_val
            else:
                scoreHi += temp_val                


        if scoreLow >= oldScoreLow and len(points) < 1000:
            temp_point = requests.post(base_url + "/RandomPointsInsidePolygon", json={"polygon": mask_polygon,
                                                                                      "n": 100}).json()
            points.extend(temp_point)
        elif scoreLow <= oldScoreLow and len(points) > 500 and sound_time > 0:
            del points[0:50]
            
        voronoi_regions = requests.post(base_url + "/ClippedVoronoi", json={"polygon": mask_polygon,
                                                                            "points": points}).json()

        for region in voronoi_regions:
            p = createShape()
            p.beginShape()
            [p.vertex(x, y) for x, y in region]
            p.endShape(CLOSE)
            shape(p)
                    
        print(videoExport.getCurrentTime())
        videoExport.saveFrame()
