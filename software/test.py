#!/usr/bin/env python

import cv2
import numpy as np
from matplotlib import pyplot as plt
import math
import os
import sys
import itertools

def dist(p0, p1):
    return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)

# def overlap(c1, c2):
# 	return dist(c1[0],c2[0]) < (c1[1]+c2[1])

# def merge_circles(c1,c2):
# 	c = c1
# 	total_radius = c1[1] + c2[1]
# 	dx = abs(c1[0][0] - c2[0][0])
# 	dy = abs(c1[0][1] - c2[0][1])
# 	new_x = c1[0][0] + int(dx*c2[1]/total_radius)
# 	new_y = c1[0][1] + int(dy*c2[1]/total_radius)
# 	c = ((new_x,new_y),total_radius)
# 	return c

# Draws track along cones
def drawTrack(img, cones):

	# No cones found, no need to draw track
	if not len(cones):
		return img

	# Init vars
	track_img = img.copy() # New image
	height, width = track_img.shape[:2] #Get size
	max_possible_distance = dist((0,0),(width,height)) # Get diagonal
	color = (0,0,0) # White
	last_slope = 0
	total_curve = 0
	first = True

	# Test left side
	cone = 0
	point = (0,height)
	min_distance = max_possible_distance
	for c in xrange(0,len(cones)):
	    dis = dist(point, cones[c][0])
	    if dis < min_distance:
	    	min_distance = dis
	    	cone = c

	# Save left start data
	min_dist_left = min_distance
	near_cone_left = cone

	# Test right side
	cone = 0
	point = (width,height)
	min_distance = max_possible_distance
	for c in xrange(0,len(cones)):
	    dis = dist(point, cones[c][0])
	    if dis < min_distance:
	    	min_distance = dis
	    	cone = c

	# Select starting side
	if min_distance > min_dist_left:
		print "Starting left"
		cone = near_cone_left
	else:
		print "Starting right"

	# Set starting cone
	point = cones[cone][0]
	cones.pop(cone)

	# Connect all cones
	while len(cones):

		# Get closest cone to current
		min_distance = max_possible_distance
		for c in xrange(0,len(cones)):
		    dis = dist(point, cones[c][0])
		    if dis < min_distance:
		    	min_distance = dis
		    	cone = c

		# Get slope
		slope = (point[1] - cones[cone][0][1])/float((cones[cone][0][0] - point[0]))
		print "Slope from cone at (" + str(point) + ") -> (" + str(cones[cone][0]) + ") = " + str(slope)
		# if float(cones[cone][0][0] - point[0]):
			# slope = (point[1] - cones[cone][0][1])/float((cones[cone][0][0] - point[0]))
		# else:
			# slope = 10

		# Slope calculations
		if first:
			ds = 0
			first = False
		else:
			ds = slope - last_slope
		last_slope = slope
		total_curve+=ds
		print "ds: " + str(ds)
		print "Total Curve: " + str(total_curve)
		print
		# print "slope: " + str(slope) + ' ',
		# if slope  > .7:
		# 	# print "straight"
		# 	color = (0,255,0)
		# elif 0.5 < slope <= .7:
		# 	# print "slant left"
		# 	color = (255,0,0)
		# elif 0.2 < slope <= 0.5:
		# 	if dist(point,cones[cone][0]) > 150:
		# 		# print dist(point,cones[cone][0])
		# 		# print "hard left - cross track"
		# 		color = (255,255,255)
		# 	else:
		# 		# print "hard left"
		# 		color = (0,0,255)
		# elif -0.2 < slope <= 0.2:
		# 	if dist(point,cones[cone][0]) > 150:
		# 		# print dist(point,cones[cone][0])
		# 		# print "horizontal - cross track"
		# 		color = (255,255,255)
		# 	else:
		# 		# print "horizontal - curved track"
		# 		color = (0,0,255)
		# elif -0.5 < slope <= -0.2:
		# 	if dist(point,cones[cone][0]) > 150:
		# 		# print dist(point,cones[cone][0])
		# 		# print "hard right - cross track"
		# 		color = (255,255,255)
		# 	else:
		# 		# print "hard right"
		# 		color = (0,0,255)
		# elif -.7 < slope <= -.5:
		# 	# print "slant right"
		# 	color = (255,0,0)
		# else:
		# 	# print "straight"
		# 	color = (0,255,0)
		# # if point[0] < center and cones[cone][0][0] < center:
		# 	cv2.line(track_img,point,cones[cone][0],color,2)
		# elif point[0] > center and cones[cone][0][0] > center:
		# 	cv2.line(track_img,point,cones[cone][0],color,2)
		# else:
		# 	if dist(point,cones[cone][0]) > 100:
		# 		color = color
		# 	else:
		cv2.line(track_img,point,cones[cone][0],color,2)
		# center = max(point[0],cones[cone][0])
		point = cones[cone][0]
		cones.pop(cone)
	return track_img

def filterOrange(img):

	# Play with these to filter
	lower = np.array([0,90,100])
	upper = np.array([5,255,255])

	hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	mask = cv2.inRange(hsv, lower, upper)
	return cv2.bitwise_and(img, img, mask = mask)

def getCones(img):
	cones = []
	cones_real = []
	gry = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

	contours, _ = cv2.findContours(gry, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

	for cnt in contours:
		if cv2.arcLength(cnt,True) > 50:
			(x,y),radius = cv2.minEnclosingCircle(cnt)
			center = (int(x),int(y))
			radius = int(radius)
			cones.append((center, radius))

	# Combine overlaps
	# print "cone len" + str(len(cones))
	# for c1_idx in xrange(0,len(cones)):
	# 	print
	# 	print "c1 " + str(c1_idx) + " of " + str(len(cones))
	# 	print
	# 	for c2_idx in xrange(c1_idx+1,len(cones)-1):
	# 		print "c2 " + str(c2_idx) + " of " + str(len(cones))
	# 		if overlap(cones[c1_idx], cones[c2_idx]):
	# 			print "overlap detected"
	# 			# cones[c1_idx] = merge_circles(cones[c1_idx],cones[c2_idx])
	# 			cones.pop(c2_idx)
	# 			c2_idx -= 1
	return cones



# Main
# Get terminal size (For reasons)
rows, columns = os.popen('stty size', 'r').read().split()
total_bars = int(columns) - 5

# Get args
pics_dir = '../vision/conez/'
if len(sys.argv) > 1:
	image = 'conez' + sys.argv[1] + '.png'
	pics = [image]
	print 'Using image ' + image
else:
	pics = os.listdir(pics_dir)

# Process
p_idx = 0
for p in pics:
	p_idx+=1
	# Get image
	frame = cv2.imread(os.path.join(pics_dir,p))
	if frame is None:
		print 'Image '+ p + ' not found'
		continue

	# Threshold
	thresh = filterOrange(frame)

	# Cone Detection
	cones = getCones(thresh)
	num_cones = len(cones)

	# Draw Cones
	cone_img = frame.copy()
	for c in cones:
		cv2.circle(cone_img,c[0],c[1],(0,255,0),2)


	# Draw Track
	track = drawTrack(frame, cones)

	# Plot
	plt.subplot(221),plt.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
	plt.title('Original'), plt.xticks([]), plt.yticks([])
	plt.subplot(222),plt.imshow(cv2.cvtColor(thresh, cv2.COLOR_BGR2RGB))
	plt.title('Threshold'), plt.xticks([]), plt.yticks([])
	plt.subplot(223),plt.imshow(cv2.cvtColor(cone_img, cv2.COLOR_BGR2RGB))
	plt.title('Cone Detection n=' + str(num_cones)), plt.xticks([]), plt.yticks([])
	plt.subplot(224),plt.imshow(cv2.cvtColor(track, cv2.COLOR_BGR2RGB))
	plt.title('Track Detection'), plt.xticks([]), plt.yticks([])
	plt.savefig('results/Result' + p)

	# Reasons
	completion = int(100*p_idx/len(pics))
	sys.stdout.write("\r" + "="*int(total_bars*completion/100.0) + ">"+ str(completion) + '%')
	sys.stdout.flush()

# Reasons cleanup
sys.stdout.write("\r" + "="*int(total_bars/2-4) + "Completed\n")
sys.stdout.flush()

