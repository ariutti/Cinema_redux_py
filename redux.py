#!/usr/bin/env python3

# Cinema Redux
# Created by Davide Bonafede
# modified by Nicola Ariutti

import cv2
import time, math
import numpy as np

# an A3 sheet # 300 dpi has a width of 3508 and a height of 4960 pixels
# an A3 sheet @ 600 dpi has a width of 7016 and a height of 9920 pixels
# So we must find a way to rescale the movie frame inorder to compress its
# duration inside this container and consenquantly calculate a new width and heigh
# for the frame to be rescaled in order to fill the entire A3 sheet approximately.
containerSize = [3508, 4960]
nFrameforLine = 20

#Video file importing
#vidcap = cv2.VideoCapture('/path/to/video')
#vidcap = cv2.VideoCapture('/home/nicola/Video/_film/Sinuhe l-egiziano- -1954- con Edmund Purdom - Jean Simmons - Film Completo ITA.mp4')
#vidcap = cv2.VideoCapture('/home/nicola/Video/_film/Carnage Ita Eng 576p.mkv')

#vidcap = cv2.VideoCapture('/media/nicola/MYPASSPORT/Filmati/The Lego Movie (2014).ita.eng.sub.ita.eng.MIRCrew/The Lego Movie (2014).ita.eng.sub.ita.eng.MIRCrew.avi')

#vidcap = cv2.VideoCapture('/home/nicola/Video/_film/Labyrinth - Dove Tutto è Possibile (1986).ita.eng.sub.ita.eng.MIRCrew.avi')
#vidcap = cv2.VideoCapture('/home/nicola/Video/_film/Viaggio Allucinante - Fantastic Voyage (1966).avi')
#vidcap = cv2.VideoCapture('/home/nicola/Video/_film/Atmosfera Zero - Outland 1981/Atmosfera Zero.mp4')
#vidcap = cv2.VideoCapture('/home/nicola/Video/_film/TH3 THR33 C4B4LL3R05 [DVDRip Xvid - ITA ENG FRA NLD MP3] [Skart].avi')
#vidcap = cv2.VideoCapture("/home/nicola/Video/_film/Ogni Cosa E' Illuminata.avi")
#vidcap = cv2.VideoCapture("/home/nicola/Video/_film/Nemico pubblico (William Wellman, 1931) James Cagney, Jean Harlow. Xvid - ITA_ENG (dual audio) [DVDrip 528x384 - 1067Kbps].avi")
#vidcap = cv2.VideoCapture("/home/nicola/Video/_film/Interstellar.mkv")
#filename = "/home/nicola/Video/_film/Federico Fellini-Amarcord (1973).avi"
filename = "/home/nicola/Video/_film/La spada nella roccia.mp4"

vidcap = cv2.VideoCapture(filename)

count = 0
success = True
firstLine = 1

def getVideoProps( cap ):
	# https://stackoverflow.com/questions/49048111/how-to-get-the-duration-of-video-using-cv2
	fps = cap.get(cv2.CAP_PROP_FPS)      # OpenCV2 version 2 used "CV_CAP_PROP_FPS"
	frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
	duration = frame_count/fps
	frame_width = cap.get( cv2.CAP_PROP_FRAME_WIDTH )
	frame_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT )

	print('fps = ' + str(fps))
	print('number of frames = ' + str(frame_count))
	print('duration (S) = ' + str(duration))
	minutes = int(duration/60)
	seconds = duration%60
	print('duration (M:S) = ' + str(minutes) + ':' + str(seconds))
	print('frame dimensione [{} x {}]'.format(frame_width, frame_height))
	return fps, frame_count, duration, frame_width, frame_height

def calculate( nHorizontalFrames, frameCount, movieDuration, originalFrameWidth, originalFrameHeight, containerWidth, containerHeight ):
	frameWithRescaled  = int(containerWidth / nHorizontalFrames);
	frameHeightRescale = int( (frameWithRescaled*originalFrameHeight) / originalFrameWidth)
	print("rescaled frame dimensions [{} x {}]".format(frameWithRescaled, frameHeightRescale))
	frameDrop=1
	newFrameCount = frameCount
	# now we must check how many lines of frames will lay inside the container
	# if too many lines are there, we must drop more frames
	outputHeight = (frameCount / nHorizontalFrames) * frameHeightRescale
	while outputHeight >= containerHeight:
		frameDrop += 1
		newFrameCount = math.ceil(frameCount / frameDrop)
		outputHeight = (newFrameCount / nHorizontalFrames) * frameHeightRescale
		#print("frameDrop {} - new frame count {} - outputHeight {}".format(frameDrop, newFrameCount, outputHeight))

	print("we are going to save {} frames taking one of them each {} frames, obtaining a final image of size[{}x{}]".format(newFrameCount, frameDrop, nHorizontalFrames*frameWithRescaled, outputHeight))
	return frameWithRescaled, frameHeightRescale, frameDrop, newFrameCount


# width and heigth of resized frames
#w = 150
#h = 84
z = 0
#oneFrameEvery = 120
success,image = vidcap.read()


fps, frame_count, duration, frame_width, frame_height = getVideoProps( vidcap )
w, h, oneFrameEvery, newFrameCount = calculate( nFrameforLine, frame_count, duration, frame_width, frame_height, containerSize[0], containerSize[1])

while success:

	if(count % oneFrameEvery == 0):
		print("{}) Saving frame {} of {}".format(count, count/oneFrameEvery, newFrameCount))
		image = cv2.resize(image, (w, h))	# image resize
		if z == 0:							# first image of the line
			imageLine = image
			z += 1
		else:
			imageLine = np.concatenate((imageLine, image), axis=1)
			z += 1
			if z == nFrameforLine:			# the line is finished
				if firstLine:
					Image = imageLine
					firstLine = 0
					z = 0
				else:
					Image = np.concatenate((Image, imageLine), axis=0)
					z = 0

	success,image = vidcap.read()
	count += 1


# fill with black missing frames to complete image
print("filling gaps with black")
for x in range(nFrameforLine - z):
	imageLine = np.concatenate((imageLine, np.zeros((h,w,3), np.uint8)), axis=1)
Image = np.concatenate((Image, imageLine), axis=0)

print("writing image")
# https://docs.opencv.org/2.4/modules/highgui/doc/reading_and_writing_images_and_video.html
# https://docs.opencv.org/master/d4/da8/group__imgcodecs.html#ga292d81be8d76901bff7988d18d2b42ac
cv2.imwrite("La_spada_nella_roccia_2.jpg", Image, [cv2.IMWRITE_JPEG_QUALITY, 100])
cv2.imwrite("La_spada_nella_roccia_2.png", Image, [cv2.IMWRITE_PNG_COMPRESSION,0])
