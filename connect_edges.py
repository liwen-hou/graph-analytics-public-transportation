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

def store_edges(num_edges):
	graph = load_graph('nodes.graphml')
	os.chdir('./edges')
	i = num_edges
	filename = str(i) + '.csv'
	with open(filename,'wb') as result:
		writer = csv.writer(result,delimiter=',')
		header = ['Node1','Node2','Distance']
		writer.writerow(header)
		for i in range(num_edges,num_edges+500):
			e = graph.vertex(i)
			if graph.vp.Type[e] != 'Post Code':
				pass
			else:
				lon1 = float(graph.vp.Longitude[e])
				lat1 = float(graph.vp.Latitude[e])
				for v in graph.vertices():
					if graph.vp.Type[v] != 'Post Code':
						pass
					else:
						lon2 = float(graph.vp.Longitude[v])
						lat2 = float(graph.vp.Latitude[v])
						dist = round(haversine(lon1,lat1,lon2,lat2),3)
						if dist < 0.2:
							row = [i,v,dist]
							writer.writerow(row)

if __name__ == '__main__':
	index = int(sys.argv[1])
	store_edges(index)
