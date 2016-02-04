from graph_tool.all import *
from itertools import tee, izip
import csv
import os, sys
import xml.etree.cElementTree as ET
from collections import defaultdict
from math import radians, cos, sin, asin, sqrt
import operator
import graph_tool.all as gt

services = defaultdict(list)
bus_stops = defaultdict(list)
mrts = defaultdict(list)
lines = defaultdict(list)
nodes = defaultdict(list)
posts = defaultdict(list)
edges = list()

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


#Return a pair of consecutive lines from some iterable

def current_and_next(some_iterable):
	
	current_row, next_row = tee(some_iterable)
	next(next_row, None)
	return izip(current_row, next_row)

#Create nodes for postal code locations

def add_post_code(filename):
	global posts
	
	with open (filename) as post_code:
		reader = csv.DictReader(post_code,delimiter = ';')
		for row in reader:
			if row['PostCode'] != None and row['Longtitude'] != None and row['Latitude'] != None :
				if len(row['PostCode']) != 6:
					for i in range(0,6-len(row['PostCode'])):
						row['PostCode'] = '0' + row['PostCode']
				posts[row['PostCode']] = dict()
				posts[row['PostCode']]['Location'] = row['Address,Region']
				posts[row['PostCode']]['Longitude'] = row['Longtitude']
				posts[row['PostCode']]['Latitude'] = row['Latitude']	


#Add the unknown stops to the graph

def add_unknown_node(unknown):
	global bus_stops
	osm_file = open('singapore.osm', "r")
	stops = list()
	for event, elem in ET.iterparse(osm_file, events=("start",)):
		d = dict()		
		if elem.tag == "node":
			d['Latitude'] = elem.attrib['lat']
			d['Longitude'] = elem.attrib['lon']
		for tag in elem.iter("tag"):
			if tag.attrib['k'] == 'asset_ref' and tag.attrib['v'].isdigit():
				d['name'] = tag.attrib['v']
			elif tag.attrib['k'] == 'name':
				d['Location'] = tag.attrib['v']
		if len(d) == 4:
			stops.append(d)
	
	for stop in unknown:
		for elem in stops:
			if stop == elem['name']:
				bus_stops[elem['name']] = dict()
				bus_stops[elem['name']]['Location'] = elem['Location']
				bus_stops[elem['name']]['Longitude'] = elem['Longitude']
				bus_stops[elem['name']]['Latitude'] = elem['Latitude']

#Read Bus Stop Files and add bus stops as nodes

def read_bus_stop_file(filename):
	global lines, bus_stops
	with open (filename) as stop_file:
		reader = csv.DictReader(stop_file)
		all_stops = defaultdict(list)
		for row in reader:
			
			if row['Node'].isdigit() and len(row['Node']) == 4:
				row['Node'] = '0' + row['Node']
			if row['Node'].isdigit():
				all_stops[row['Node']] = dict()
				all_stops[row['Node']]['Location'] = row['Info1']
				all_stops[row['Node']]['Longitude'] = row['Long']
				all_stops[row['Node']]['Latitude'] = row['Lat']
			if row['Node'].isdigit() == False:
				mrt_code = list()
				mrt_code = row['Info1'].split('/')
				for item in mrt_code:
						lines[item[:2]].append(row)

	unknown = list()
	os.chdir('./SBST')
	for file_name in os.listdir(os.getcwd()):
		if file_name.endswith('.csv'):
			with open(file_name) as route:
				reader2 = csv.DictReader(route,fieldnames=['1','stop_no','distance','express','arr_time','dep_time','last_bus','ID','direction','service_no'])
				for row in reader2:
					bus_stops[row['stop_no']] = dict()
	os.chdir('../SMRT')
	for file_name in os.listdir(os.getcwd()):
		if file_name.endswith('.csv'):
			with open(file_name) as route:
				reader2 = csv.DictReader(route,fieldnames=['1','stop_no','distance','express','arr_time','dep_time','last_bus','ID','direction','service_no'])
				for row in reader2:
					bus_stops[row['stop_no']] = dict()
	
	os.chdir('../')
	for key in bus_stops:
		if key in all_stops:
			bus_stops[key]['Location'] = all_stops[key]['Location']
			bus_stops[key]['Longitude'] = all_stops[key]['Longitude']
			bus_stops[key]['Latitude'] = all_stops[key]['Latitude']
		else:
			unknown.append(key)
	return unknown
		
				
#add MRT stations as nodes

def add_MRT():
	for line in lines:
		#print line
		for station in lines[line]:
			#print station
			mrt_code = station['Info1'].split('/')
			for item in mrt_code:
					
				if item[:2] == line:
					#print station['Info1']
					mrt_name = station['Node'] +' ' + line
					mrts[mrt_name] = dict()
					mrts[mrt_name]['Location'] = station['Info1']
					mrts[mrt_name]["Longitude"] = station['Long']
					mrts[mrt_name]["Latitude"] = station['Lat']

					#g.add_vertices(1)
					#g.vs[count]["name"] = station['Node'] +' ' + line + ' 2'
					#g.vs[count]["Location"] = station['Info1']
					#g.vs[count]["Longitude"] = station['Long']
					#g.vs[count]["Latitude"] = station['Lat']
					#count += 1
					station['no'] = int(item[2:])	

	mrts['Punggol PTC'] = dict()
	mrts['Punggol PTC']['Location'] = 'PTC'
	mrts['Punggol PTC']["Longitude"] = mrts['Punggol NE']["Longitude"]
	mrts['Punggol PTC']["Latitude"] = mrts['Punggol NE']["Latitude"] 

	mrts['Sengkang STC'] = dict()
	mrts['Sengkang STC']['Location'] = 'STC'
	mrts['Sengkang STC']["Longitude"] = mrts['Sengkang NE']["Longitude"]
	mrts['Sengkang STC']["Latitude"] = mrts['Sengkang NE']["Latitude"]
	


def init_graph():
	global bus_stops, mrts, nodes, posts
	graph = Graph()
	graph.vp.name = graph.new_vertex_property('string')
	graph.vp.Type = graph.new_vertex_property('string')
	graph.vp.Index = graph.new_vertex_property('int')
	graph.vp.Location = graph.new_vertex_property('string')
	graph.vp.Latitude = graph.new_vertex_property('string')
	graph.vp.Longitude = graph.new_vertex_property('string')
	for items in bus_stops:
		nodes[items] = dict()
		nodes[items]['Type'] = 'Bus Stop'
		nodes[items]['Location'] = bus_stops[items]['Location']
		nodes[items]['Longitude'] = bus_stops[items]['Longitude']
		nodes[items]['Latitude'] = bus_stops[items]['Latitude']
	for items in mrts:
		nodes[items] = dict()
		nodes[items]['Type'] = 'MRT Stop'
		nodes[items]['Location'] = mrts[items]['Location']
		nodes[items]['Longitude'] = mrts[items]['Longitude']
		nodes[items]['Latitude'] = mrts[items]['Latitude']
	for items in posts:
		nodes[items] = dict()
		nodes[items]['Type'] = 'Post Code'
		nodes[items]['Location'] = posts[items]['Location']
		nodes[items]['Longitude'] = posts[items]['Longitude']
		nodes[items]['Latitude'] = posts[items]['Latitude']
	i = 0
	for item in nodes:
		index = graph.add_vertex()
		nodes[item]['Index'] = i
		graph.vp.name[index] = item
		graph.vp.Index[index] = i
		graph.vp.Type[index] = nodes[item]['Type']
		graph.vp.Location[index] = nodes[item]['Location']
		graph.vp.Latitude[index] = nodes[item]['Latitude']
		graph.vp.Longitude[index] = nodes[item]['Longitude']
		i += 1

	return graph





if __name__ == '__main__':
	
	unknown = read_bus_stop_file('info.csv')

	add_unknown_node(unknown)
	add_MRT()
	os.chdir('./ZXPostCode')
	for file_name in os.listdir(os.getcwd()):
		if file_name.endswith('.csv'):
			add_post_code(file_name)
	os.chdir('../')

	#delete empty stops
	delete_stop = list()
	for stop in bus_stops:
		if not bus_stops[stop]:
			delete_stop.append(stop)
	for stop in delete_stop:
		del bus_stops[stop]

	graph = init_graph()

	graph.save('nodes.graphml')

	#calculate_centrality(graph)