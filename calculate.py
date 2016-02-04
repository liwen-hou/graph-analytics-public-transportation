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
	cl_unweighted = gt.closeness(graph)
	cl_distance = gt.closeness(graph,weight=graph.ep.Distance)
	bt_unweighted, ep = gt.betweenness(graph)
	bt_distance, ep = gt.betweenness(graph,weight=graph.ep.Distance)
	cl_time = gt.closeness(graph,weight=graph.ep.Time)
	bt_time, ep = gt.betweenness(graph,weight=graph.ep.Time)

	f = open('cl_time.txt', 'w+')
	f = open('cl_time.txt', 'r+')
	f.writelines(["%s\n" % item  for item in cl_time.a])
	f = open('bt_time.txt', 'w+')
	f = open('bt_time.txt', 'r+')
	f.writelines(["%s\n" % item  for item in bt_time.a])
	f = open('cl_unweighted.txt', 'w+')
	f = open('cl_unweighted.txt', 'r+')
	f.writelines(["%s\n" % item  for item in cl_unweighted.a])
	f = open('cl_distance.txt', 'w+')
	f = open('cl_distance.txt', 'r+')
	f.writelines(["%s\n" % item  for item in cl_distance.a])
	f = open('bt_unweighted.txt', 'w+')
	f = open('bt_unweighted.txt', 'r+')
	f.writelines(["%s\n" % item  for item in bt_unweighted.a])
	f = open('bt_distance.txt', 'w+')
	f = open('bt_distance.txt', 'r+')
	f.writelines(["%s\n" % item  for item in bt_distance.a])

	with open('results_time.csv','wb') as results:
		writer = csv.writer(results,delimiter=',')
		header = ['Name','Type','Longitude','Latitude','Closeness_Unweighted','Closeness_Distance','Betweenness_Unweighted','Betweenness_Distance','Closeness_Time','Betweenness_Time']
		writer.writerow(header)
		for v in graph.vertices():
			row = [graph.vp.name[v],graph.vp.Type[v],graph.vp.Longitude[v],graph.vp.Latitude[v],cl_unweighted[v],cl_distance[v],bt_unweighted[v],bt_distance[v],cl_time[v],bt_time[v]]
			writer.writerow(row)

if __name__ == '__main__':

	graph = load_graph('w_time_sg_graph.graphml')

	calculate_centrality(graph)