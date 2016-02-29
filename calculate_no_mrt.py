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
	print 'calculate betweenness'
	bt_time, ep = gt.betweenness(graph,weight=graph.ep.Time)

	f = open('cl_no_mrt.txt', 'w+')
	f = open('cl_no_mrt.txt', 'r+')
	f.writelines(["%s\n" % item  for item in cl_time.a])
	f = open('bt_no_mrt.txt', 'w+')
	f = open('bt_no_mrt.txt', 'r+')
	f.writelines(["%s\n" % item  for item in bt_time.a])

	with open('results_no_mrt.csv','wb') as results:
		writer = csv.writer(results,delimiter=',')
		header = ['Name','Type','Longitude','Latitude','Closeness_Time','Betweenness_Time']
		writer.writerow(header)
		for v in graph.vertices():
			row = [graph.vp.name[v],graph.vp.Type[v],graph.vp.Longitude[v],graph.vp.Latitude[v],cl_time[v],bt_time[v]]
			writer.writerow(row)

if __name__ == '__main__':

	graph = load_graph('no_mrt.graphml')
	print 'graph loaded'
	e = graph.edge(27708, 50784)
	graph.ep.Time[e] = 19
	e = graph.edge(34443, 4809)
        graph.ep.Time[e] = 30
	e = graph.edge(35959, 3795)
        graph.ep.Time[e] = 13
	e = graph.edge(52581, 3795)
        graph.ep.Time[e] = 14
	e = graph.edge(55528, 107676)
        graph.ep.Time[e] = 7
	e = graph.edge(85097, 4809)
        graph.ep.Time[e] = 22
	e = graph.edge(97522, 77382)
        graph.ep.Time[e] = 6 
	e = graph.edge(125627, 45055)
        graph.ep.Time[e] = 7
	for e in graph.edges():
		if graph.ep.Time[e] < 0:
			print e, ' ', graph.ep.Time[e], ' ', graph.ep.Method[e],' ', graph.ep.Distance[e]
			graph.ep.Time[e] = 2
	print 'time adjusted'
	graph.save('no_mrt.graphml')
	print 'graph saved'
	graph = load_graph('no_mrt.graphml')
	print 'graph reloaded'
	for e in graph.edges():
                if graph.ep.Time[e] < 0:
                        print e, ' ', graph.ep.Time[e], ' ', graph.ep.Method[e],' ', graph.ep.Distance[e]
	calculate_centrality(graph)
