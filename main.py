from PIL import Image, ImageDraw
import numpy as np
import colorsys
import subprocess as sp
import numpy
import re

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

	return processImage(orig, minVal, numberOfBands, bandThresholds)
	

def processImage(image, minVal, numberOfBands, bandThresholds):
	hsv = image.convert("HSV")

	bandWidth = hsv.width / numberOfBands

	bandValues = [];

	for bandIndex in range(hsv.width / bandWidth):
		bandValues.append(processBand(hsv, minVal, bandIndex * bandWidth, bandWidth))

	draw = ImageDraw.Draw(image)

	linesYAxis  = [0 for x in range(numberOfBands)]

	bandIndex = 0
	for bandValue in bandValues:
		rowIndex = 0
		for rowValue in bandValue:
			if(rowValue > bandThresholds[bandIndex]):
				# draw.line((bandIndex * bandWidth, rowIndex, (bandIndex + 1) * bandWidth, rowIndex), "#F00", 2)
				linesYAxis[bandIndex] = rowIndex;

			rowIndex = rowIndex + 1

		bandIndex = bandIndex + 1


		# draw.line((bandIndex * bandWidth, rowIndex, (bandIndex + 1) * bandWidth, rowIndex), "#F00", 2)	
	for band in range(numberOfBands):
		if(linesYAxis[band] > 0):
			draw.line((band * bandWidth, linesYAxis[band], (band + 1) * bandWidth, linesYAxis[band]), "#F00", 2)	


	image.show()	


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
	width, height = get_size(file)

	# open video file
	command = [ 'ffmpeg', '-ss', '00:00:11', '-i', file, '-f', 'image2pipe', '-pix_fmt', 'rgb24', '-vcodec', 'rawvideo', '-']
	pipe = sp.Popen(command, stdout = sp.PIPE, bufsize=10**8)

	for x in range(30):
		raw_image = pipe.stdout.read(width*height*3)
		image_array = numpy.fromstring(raw_image, dtype=np.uint8).reshape(height, width, 3)

		image = Image.fromarray(image_array, 'RGB')

		processImage(image, 240, 2, [100, 100])

	return [width, height]




pattern = re.compile(r'Stream.*Video.*([0-9]{3,})x([0-9]{3,})')
def get_size(file):
    p = sp.Popen(['ffmpeg', '-i', file], stdout=sp.PIPE, stderr=sp.PIPE)

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

print(processVideo("vid/1.wmv"))