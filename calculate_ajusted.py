from graph_tool import *
from itertools import tee, izip
import csv
import xml.etree.cElementTree as ET
import os, sys
from collections import defaultdict
from math import radians, cos, sin, asin, sqrt
import operator
import graph_tool.all as gt

def calculate_centrality(graph):
	print 'calculate closeness'
	cl_time = gt.closeness(graph,weight=graph.ep.Time)

	f = open('cl_time_adjusted.txt', 'w+')
	f = open('cl_time_adjusted.txt', 'r+')
	f.writelines(["%s\n" % item  for item in cl_time.a])

	with open('results_time_adjusted.csv','wb') as results:
		writer = csv.writer(results,delimiter=',')
		header = ['Name','Type','Longitude','Latitude','Closeness_Time']
		writer.writerow(header)
		for v in graph.vertices():
			row = [graph.vp.name[v],graph.vp.Type[v],graph.vp.Longitude[v],graph.vp.Latitude[v],cl_time[v]]
			writer.writerow(row)

if __name__ == '__main__':

	graph = load_graph('graph_time_no_lrt.graphml')
	print 'graph loaded'
	for e in graph.edges():
		if graph.ep.Time[e] < 0:
			if graph.ep.Time[e] == -7 and graph.ep.Distance[e] == 15.3:
				graph.ep.Time[e] = 19
			elif graph.ep.Time[e] == -32 and graph.ep.Distance[e] == 6.5:
				graph.ep.Time[e] = 30
			elif graph.ep.Time[e] == -9 and graph.ep.Distance[e] == 7.4:
				graph.ep.Time[e] = 13
			elif graph.ep.Time[e] == -24 and graph.ep.Distance[e] == 9.3:
				graph.ep.Time[e] = 14
			elif graph.ep.Time[e] == -6 and graph.ep.Distance[e] == 4.7:
				graph.ep.Time[e] = 7
			elif graph.ep.Time[e] == -30 and graph.ep.Distance[e] == 7.1:
				graph.ep.Time[e] = 22
			elif graph.ep.Time[e] == -1 and graph.ep.Distance[e] == 4.3:
				graph.ep.Time[e] = 6
			elif graph.ep.Time[e] == -7 and graph.ep.Distance[e] == 5.3:
				graph.ep.Time[e] = 7

			print e, ' ', graph.ep.Time[e], ' ', graph.ep.Method[e],' ', graph.ep.Distance[e]
			graph.ep.Time[e] = 4
	print 'time adjusted'
	graph.save('graph_time_no_lrt.graphml')
	print 'graph saved'
	graph = load_graph('graph_time_no_lrt.graphml')
	print 'graph reloaded'
	for e in graph.edges():
                if graph.ep.Time[e] < 0:
                        print e, ' ', graph.ep.Time[e], ' ', graph.ep.Method[e],' ', graph.ep.Distance[e]
	calculate_centrality(graph)
