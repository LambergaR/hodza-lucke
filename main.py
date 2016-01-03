from PIL import Image, ImageDraw
import numpy as np
import colorsys
import subprocess as sp
import numpy
import re

import matplotlib.pyplot as plt

ffmpegCommand = "ffmpeg"

videoWidth = 854
videoHeigh = 480

def rect(pos, imageDraw, color):
	imageDraw.rectangle((pos[1] - 1, pos[2] - 1, pos[1] + 1, pos[2] + 1), fill=color)

def process(imagePath):

	orig = Image.open(imagePath)
	hsv = orig.convert("HSV")

	hueMax = [0, 0, 0]
	saturationMax = [0, 0, 0]
	valueMax = [0, 0, 0]

	hueMin = [255, 0, 0]
	saturationMin = [255, 0, 0]
	valueMin = [255, 0, 0]

	for x in range(hsv.width):
		for y in range(hsv.height):

			h, s, v = hsv.getpixel((x, y))
			# print h, s, v

			# hue
			if(h > hueMax[0]):
				hueMax = [h, x, y]

			if(s > saturationMax[0]):
				saturationMax = [s, x, y]

			if(v > valueMax[0]):
				valueMax = [v, x, y]

			if(h < hueMin[0]):
				hueMin = [h, x, y]

			if(s < saturationMin[0]):
				saturationMin = [s, x, y]

				

	draw = ImageDraw.Draw(orig)
	# draw.rectangle((satMaxX-10, satMaxY-10, satMaxX+10, satMaxY+10), fill=128)
	rect(hueMax, draw, "#F00")
	rect(saturationMax, draw, "#F00")
	rect(valueMax, draw, "#F00")

	rect(hueMin, draw, "#0F0")
	rect(saturationMin, draw, "#0F0")
	rect(valueMin, draw, "#0F0")

	orig.show()

	return 0

def multiple(imagePath):

	orig = Image.open(imagePath)
	hsv = orig.convert("HSV")

	minSat = 250

	satSpots = []

	for x in range(hsv.width):
		for y in range(hsv.height):

			h, s, v = hsv.getpixel((x, y))

			if(v > minSat):
				satSpots.append([v, x, y])

	draw = ImageDraw.Draw(orig)

	for spot in satSpots:
		rect(spot, draw, "#F00")

	orig.show()

	return satSpots

def bandClusterDetection(imagePath, minVal, numberOfBands, bandThresholds):
	orig = Image.open(imagePath)

	return processImage(orig, minVal, numberOfBands, bandThresholds, "out")
	
linesYAxisOld = [0]

def processImage(image, minVal, numberOfBands, bandThresholds, outName):

	global linesYAxisOld

	try:
		if len(linesYAxisOld) == 0:
			linesYAxisOld = [0 for x in range(numberOfBands)]
		print("intialized")
		
		pass
	except Exception, e:
		linesYAxisOld = [0 for x in range(numberOfBands)]
		print("intialized")

		pass

	print(outName)

	hsv = image.convert("HSV")

	bandWidth = hsv.width / numberOfBands

	bandValues = []

	for bandIndex in range(hsv.width / bandWidth):
		bandValue = processBand(hsv, minVal, bandIndex * bandWidth, bandWidth);
		bandValues.append(bandValue)

	draw = ImageDraw.Draw(image)

	linesYAxis  = [0 for x in range(numberOfBands)]

	bandIndex = 0
	for bandValue in bandValues:
		rowIndex = 0
		for rowValue in bandValue:
			if(rowValue > bandThresholds[bandIndex]):
				linesYAxis[bandIndex] = rowIndex;

			rowIndex = rowIndex + 1

		bandIndex = bandIndex + 1


	for band in range(numberOfBands):
		try:
			print("old: " + str(linesYAxisOld[band]) + " --  new: " + str(linesYAxis[band]))
			pass
		except Exception:
			pass

		if band < len(linesYAxisOld):
			if linesYAxis[band] < linesYAxisOld[band]:
				# something special
				linesYAxis[band] = int(linesYAxisOld[band] * 0.95)

				print("missing")

		if linesYAxis[band] > 0:
			draw.rectangle(
				[(band + 1) * bandWidth, 0, band * bandWidth,  linesYAxis[band]],
				"#0033cc",
				2
			)	
			# draw.line(
			# 	(band * bandWidth, linesYAxis[band], (band + 1) * bandWidth, linesYAxis[band]), 
			# 	"#F00", 
			# 	2
			# )	

	linesYAxisOld = list(linesYAxis)

	# image.show()	
	image.save(outName + ".png", "PNG")

def processBand(hsvImage, minVal, bandStartX, bandWidth):
	bandValues = []

	for y in range(hsvImage.height):
		bandValueSum = 0

		for x in range(bandStartX, bandStartX + bandWidth):
			h, s, v = hsvImage.getpixel((x, y))

			if(v > minVal):
				bandValueSum = bandValueSum + s

		bandValues.append(bandValueSum)


	return bandValues

def processVideo(file):
	# width, height = get_size(file)
	width = videoWidth
	height = videoHeigh

	outImagePrefix = "res_img_"
	frameCount = 500

	# open video file
	command = [ ffmpegCommand, '-ss', '00:00:06', '-i', file, '-f', 'image2pipe', '-pix_fmt', 'rgb24', '-vcodec', 'rawvideo', '-']
	pipe = sp.Popen(command, stdout = sp.PIPE, bufsize=10**8)

	frameCounter = 0;

	for x in range(frameCount):
		raw_image = pipe.stdout.read(width*height*3)
		image_array = numpy.fromstring(raw_image, dtype=np.uint8).reshape(height, width, 3)

		image = Image.fromarray(image_array, 'RGB')

# , 250, 12, [200, 200, 100, 100, 50, 90, 140, 500, 500, 200, 200, 200])
		# uncomment me 
		processImage(
			image, 
			230, 
			12, 
			[40, 40, 40, 40, 40, 31, 80, 80, 80, 60, 80, 80],
			# 240, 
			# 12, 
			# [100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100],
			genOutImageName(outImagePrefix, x)
		)

		# stats = processImageForStats(image)
		# plotStats(stats)
		# writeStats(stats, "stats_" + str(frameCounter) + ".csv")

		frameCounter = frameCounter + 1

	img2video(outImagePrefix, frameCount, "result")

	return [width, height]

def genOutImageName(imgPrefix, imgIndex):
	out = imgPrefix

	if imgIndex < 10:
		out = out + "0"

	if imgIndex  < 100:
		out = out + "0"

	out = out + str(imgIndex)

	return out

def processImageForStats(hsv):
	stats = []

	for x in range(videoWidth):
		column = []

		for y in range(videoHeigh):
			h, s, v = hsv.getpixel((x, y))
			column.append(v)

		stats.append(column)

	return stats

def writeStats(stats, fileName):
	file = open(fileName, "w")
	
	for x in range(len(stats)):
		file.write("\n")
		column = stats[x]
		for y in range(len(column)):
			file.write(str(column[y]) + ", ")

	file.close()

def plotStats(stats):
	# for x in range(len(stats)):
	# 	column = stats[x]
	# 	for y in range(len(column)):

	plt.plot(stats)
	plt.show()

	return 0

def img2video(outNamePrefix, numImages, outName):
	imgNamePattern = outNamePrefix + "%03d." + "png"

	command = [ ffmpegCommand, "-r", "30/1", "-i", imgNamePattern, "-c:v", "libx264", "-vf", "fps=25", "-pix_fmt", "yuv420p", outName + "_.mp4" ]

	pipe = sp.Popen(command, stdout = sp.PIPE, bufsize=10**8)


pattern = re.compile(r'Stream.*Video.*([0-9]{3,})x([0-9]{3,})')
def get_size(file):
    p = sp.Popen([ffmpegCommand, '-i', file], stdout=sp.PIPE, stderr=sp.PIPE)

    stdout, stderr = p.communicate()
    match = pattern.search(stderr)

    if match:
        return int(match.groups()[0]), int(match.groups()[1])
    else:
        x = y = 0

    return x, y



# bandClusterDetection("img/4.jpg", 240, 4, [800, 700, 600, 40])
# bandClusterDetection("img/3.jpg", 240, 4, [800, 700, 600, 40])
# bandClusterDetection("img/2.png", 240, 4, [800, 700, 600, 40])

print(processVideo("vid/video_dolg.wmv"))
print("DONE")