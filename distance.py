from graph_tool import *
from itertools import tee, izip
import csv
import xml.etree.cElementTree as ET
import os, sys
from collections import defaultdict
from math import radians, cos, sin, asin, sqrt
import operator
import graph_tool.all as gt


#Calculate distance between two points on earth

def haversine(lon1, lat1, lon2, lat2):
	"""
	Calculate the great circle distance between two points 
	on the earth (specified in decimal degrees)
	"""
	# convert decimal degrees to radians 
	lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
	# haversine formula 
	dlon = lon2 - lon1 
	dlat = lat2 - lat1 
	a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
	c = 2 * asin(sqrt(a)) 
	km = 6367 * c
	return km

def store_dist(num_edges):
	graph = load_graph('nodes.graphml')
	os.chdir('./distances')
	i = num_edges
	filename = str(i) + '.csv'
	with open(filename,'wb') as result:
		writer = csv.writer(result,delimiter=',')
		header = ['Node','Name','Type','Longitude','Latitude','Total Distance','Closenese Centrality']
		writer.writerow(header)
		for i in range(num_edges,num_edges+500):
			e = graph.vertex(i)
			total = 0
			lon1 = float(graph.vp.Longitude[e])
			lat1 = float(graph.vp.Latitude[e])
			for v in graph.vertices():
				lon2 = float(graph.vp.Longitude[v])
				lat2 = float(graph.vp.Latitude[v])
				dist = round(haversine(lon1,lat1,lon2,lat2),3)
				total += dist
			row = [i,graph.vp.name[e],graph.vp.Type[e],lon1,lat1,total,1/total]
			writer.writerow(row)

if __name__ == '__main__':
	index = int(sys.argv[1])
	store_dist(index)
