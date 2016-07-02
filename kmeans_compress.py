import itertools
import sys
import os
from optparse import OptionParser
from PIL import Image
import random

def dist(A,B):
	dist_squared = 0.0
	for x,y in zip(A,B):
		dist_squared += (x-y)**2
	return dist_squared**0.5

def nearest_cluster(p, cluster_centers):
	shortestDistance = dist(p,cluster_centers[0])
	clusterToReturn = 0
	for k in range(1,len(cluster_centers)):
		c = cluster_centers[k]
		d = dist(p,c)
		if d < shortestDistance:
			shortestDistance = d
			clusterToReturn = k
	return clusterToReturn

def mean(v):
	return [float(x)/float(len(v)) for x in map(sum, zip(*v))]

usage = __file__ + " [options] file_path \n Here file_path is the path to the image file you wish to compress"
optparser = OptionParser(usage)
optparser.add_option("-o","--opath", dest = "opath", help = "The path of the output file", default = "./compressed_image.jpg")
optparser.add_option("-n", "--ncolors", dest = "ncolors", help = "The number of colors to be used in the compression", type = int, default=5)
(options,args) = optparser.parse_args()

try:
	fpath = args[0]	
except:
	print "you must specify a file path for the image you wish to include"
	sys.exit()

try:
	image = Image.open(fpath)
except:
	print "Couldn't open the file. Make sure the file path you provided is correct"
	sys.exit()

pix = image.load()
width = image.size[0] 
height = image.size[1]

n_colors = options.ncolors
cluster_center = [[random.random()*255.0,random.random()*255.0, random.random()*255.0] for i in range(n_colors)]
cluster_assignment = [[-1 for j in range(height)] for i in range(width)]

#go through 5 steps of the EM algorithm. Stop early if 'converged' - i.e. the clusters don't move much between iterations
for iter in range(5):
	points_per_cluster = [[] for k in range(n_colors)]
	for i,j in itertools.product(range(width),range(height)):
		best_cluster = nearest_cluster(pix[i,j],cluster_center)
		cluster_assignment[i][j] = best_cluster
		points_per_cluster[best_cluster].append(pix[i,j])
	cluster_motion = [[new_coord - old_coord for old_coord,new_coord in zip(ccent,mean(pts))] for ccent,pts in zip(cluster_center, points_per_cluster)]
	cluster_center = [mean(pts) for pts in points_per_cluster]
	if max([abs(c) for cm in cluster_motion for c in cm]) < 10: #considered convergence if the largest coordinate move among the centroids is less than e.g. 10 (10/255 ~ 4%)
		break

newPix = [tuple(map(int,cluster_center[cluster_assignment[i][j]])) for j,i in itertools.product(range(height),range(width))]
outIm = Image.new(image.mode,image.size)
outIm.putdata(newPix)

outIm.save(options.opath)
