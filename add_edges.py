from graph_tool import *
from itertools import tee, izip
import csv
import xml.etree.cElementTree as ET
import os, sys
from collections import defaultdict
from math import radians, cos, sin, asin, sqrt
import operator
import graph_tool.all as gt

def addEdges(graph):
	with open('edges.csv') as edges:
		reader = csv.DictReader(edges)
		for row in reader:
			if row['Node1'] != row['Node2']:
				edge = graph.add_edge(row['Node1'],row['Node2'])
				graph.ep.Distance[edge] = float(row['Distance'])
				graph.ep.Time[edge] = round(float(row['Distance'])/5*60,3)
				edge = graph.add_edge(row['Node2'],row['Node1'])
				graph.ep.Distance[edge] = float(row['Distance'])
				graph.ep.Time[edge] = round(float(row['Distance'])/5*60,3)

	graph.save('w_post_sg_graph.graphml')

if __name__ == '__main__':
	
	os.chdir('./all_results')

	graph = load_graph('w_time_sg_graph.graphml')

	os.chdir('../edges')

	addEdges(graph)


