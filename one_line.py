from graph_tool import *
from itertools import tee, izip
import csv
import xml.etree.cElementTree as ET
import os, sys
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
"""
--------------------Calculate distance between two points on earth----------------------------------
"""
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

"""
----------------------------------------------------------------------------------------------------
"""
"""
------------------------Return a pair of consecutive lines from some iterable-----------------------
"""
def current_and_next(some_iterable):
	
	current_row, next_row = tee(some_iterable)
	next(next_row, None)
	return izip(current_row, next_row)

"""
----------------------------------------------------------------------------------------------------
"""

"""
------------------------Create nodes for postal code locations-----------------------
"""
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
"""
----------------------------------------------------------------------------------------------------
"""

"""
-----------Find bus stops that are in the bus route files but not the bus stop files----------------
"""
def find_unknown_node():
	busStop = list()
	with open('info.csv') as stops:
		reader1 = csv.DictReader(stops)
		for row in reader1:
			if row['Node'].isdigit() and len(row['Node']) == 4:
				row['Node'] = '0' + row['Node']
			busStop.append(row['Node'])

	unknown = list()
	os.chdir('./SBST')
	for file_name in os.listdir(os.getcwd()):
		if file_name.endswith('.csv'):
			with open(file_name) as route:
				reader2 = csv.DictReader(route,fieldnames=['1','stop_no','distance','express','arr_time','dep_time','last_bus','ID','direction','service_no'])
				for row in reader2:
					if row['stop_no'] not in busStop and row['stop_no'] not in unknown:
						unknown.append(row['stop_no'])
	os.chdir('../SMRT')
	for file_name in os.listdir(os.getcwd()):
		if file_name.endswith('.csv'):
		        with open(file_name) as route:
		                reader2 = csv.DictReader(route,fieldnames=['1','stop_no','distance','express','arr_time','dep_time','last_bus','ID','direction','service_no'])
		                for row in reader2:
		                        if row['stop_no'] not in busStop and row['stop_no'] not in unknown:
		                                unknown.append(row['stop_no'])
	os.chdir('../')

	return unknown

"""
----------------------------------------------------------------------------------------------------
"""

"""
--------------------------------Add the unknown stops to the graph---------------------------------------------
"""
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


"""
----------------------------------------------------------------------------------------------------
"""

"""
-----------------------------Read Bus Stop Files and add bus stops as nodes--------------------------
"""
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
		
			
"""
----------------------------------------------------------------------------------------------------
"""


"""
------------------------------------add MRT stations as nodes-----------------------------------------
"""
def add_MRT():
	del lines['BP']
	del lines['PW']
	del lines['PE']
	del lines['SW']
	del lines['SE']
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
	
"""
----------------------------------------------------------------------------------------------------
"""

"""
------------------------------------add bus services as edges-----------------------------------------
"""
def read_route_file(filename, g):
	global services
	with open (filename) as route:
		reader = csv.DictReader(route,fieldnames=['1','stop_no','distance','express','first_bus','dep_time','last_bus','ID','direction','service_no'])
		for current_row, next_row in current_and_next(reader):
			if current_row['stop_no'].isdigit() and len(current_row['stop_no']) == 4:
				current_row['stop_no'] = '0' + current_row['stop_no']
			if next_row['stop_no'].isdigit() and len(next_row['stop_no']) == 4:
				next_row['stop_no'] = '0' + next_row['stop_no']

			if current_row['direction'] == next_row['direction']:
				if (current_row['distance'] == '-' or current_row['express'] == 'N') and (next_row['distance'] == '-' or next_row['express'] == 'N'):
					pass;
				elif (current_row['distance'] != '-' and current_row['express'] != 'N') and (next_row['distance'] == '-' or next_row['express'] == 'N'):
					stop1 = dict()
					stop1 = current_row
				elif (current_row['distance'] != '-' and current_row['express'] != 'N') and (next_row['distance'] != '-' and next_row['express'] != 'N'):	
					a = nodes[current_row['stop_no']]['Index']
					b = nodes[next_row['stop_no']]['Index']					
					
					if g.edge(a,b) == None:
						edge = g.add_edge(a,b)
						dist = float(next_row['distance']) - float(current_row['distance'])
						g.ep.Distance[edge] = float(round(dist,2))
						g.ep.Method[edge] = current_row['service_no']
						if current_row['first_bus'].isdigit():
							arr_time1 = int(current_row['first_bus'])
							arr_time2 = int(next_row['first_bus'])
							min2 = arr_time2/100*60 + arr_time2%100
							min1 = arr_time1/100*60 + arr_time1%100
						elif current_row['last_bus'].isdigit():
							arr_time1 = int(current_row['last_bus'])
							arr_time2 = int(next_row['last_bus'])
							min2 = arr_time2/100*60 + arr_time2%100
							min1 = arr_time1/100*60 + arr_time1%100
						else:
							arr_time1 = int(current_row['dep_time'])
							arr_time2 = int(next_row['dep_time'])
							min2 = arr_time2/100*60 + arr_time2%100
							min1 = arr_time1/100*60 + arr_time1%100
						g.ep.Time[edge] = (min2 - min1) * 2
					else:
						edge = g.edge(a,b)
						g.ep.Method[edge] += ' ' + current_row['service_no']

					
					#g.es[count]["direction"] = current_row['direction']
					#g.es[count]["service_no"] = current_row['service_no']
					
				elif (current_row['distance'] == '-' or current_row['express'] == 'N') and (next_row['distance'] != '-' and next_row['express'] != 'N'):				
					a = nodes[stop1['stop_no']]['Index']
					b = nodes[next_row['stop_no']]['Index']	

					if g.edge(a,b) == None:
						edge = g.add_edge(a,b)
						dist = float(next_row['distance']) - float(stop1['distance'])
						g.ep.Distance[edge] = float(round(dist,2))
						g.ep.Method[edge] = current_row['service_no']
						if stop1['first_bus'].isdigit():
							arr_time1 = int(stop1['first_bus'])
							arr_time2 = int(next_row['first_bus'])
							min2 = arr_time2/100*60 + arr_time2%100
							min1 = arr_time1/100*60 + arr_time1%100
						elif stop1['last_bus'].isdigit():
							arr_time1 = int(stop1['last_bus'])
							arr_time2 = int(next_row['last_bus'])
							min2 = arr_time2/100*60 + arr_time2%100
							min1 = arr_time1/100*60 + arr_time1%100
						else:
							arr_time1 = int(stop1['dep_time'])
							arr_time2 = int(next_row['dep_time'])
							min2 = arr_time2/100*60 + arr_time2%100
							min1 = arr_time1/100*60 + arr_time1%100
						g.ep.Time[edge] = (min2 - min1) * 2
						
					else:
						edge = g.edge(a,b)
						g.ep.Method[edge] += ' ' + current_row['service_no']		
					#print stop1
					#print next_row
					
					#g.es[count]["direction"] = stop1['direction']
					#g.es[count]["service_no"] = stop1['service_no']
				
	return g
"""
----------------------------------------------------------------------------------------------------
"""

"""
------------------------------------connect bus stops with MRT-----------------------------------------
"""
def connect_bus_MRT(graph):
	global mrts, bus_stops, nodes
	for mrt in mrts:
		lon1 = float(mrts[mrt]['Longitude'])
		lat1 = float(mrts[mrt]['Latitude'])
		for bus in bus_stops:
				
			lon2 = float(bus_stops[bus]['Longitude'])
			lat2 = float(bus_stops[bus]['Latitude'])
			dist = round(haversine(lon1, lat1, lon2, lat2),3)
								
			if dist < 0.5:
					
				edge1 = graph.add_edge(nodes[mrt]['Index'],nodes[bus]['Index'])
				edge2 = graph.add_edge(nodes[bus]['Index'],nodes[mrt]['Index'])
				graph.ep.Distance[edge1] = dist * 1.5
				graph.ep.Method[edge1] = 'Walking'
				graph.ep.Time[edge1] = round(dist*1.5/5*60,3)
				graph.ep.Distance[edge2] = dist * 1.5
				graph.ep.Method[edge2] = 'Walking'
				graph.ep.Time[edge2] = round(dist*1.5/5*60,3)
	return graph	

"""
----------------------------------------------------------------------------------------------------
"""	
"""
------------------------------------connect MRT-----------------------------------------
"""
def connect_MRT(graph,temp):

	os.chdir('./MRT')
	for file_name in os.listdir(os.getcwd()):
		if file_name == (temp + '.csv') or (temp == 'EW' and file_name == 'CG.csv') or (temp == 'CC' and file_name == 'CE.csv'):
			with open (file_name) as mrt_route:
				reader = csv.DictReader(mrt_route,fieldnames=['name','seq'])
				for current_row, next_row in current_and_next(reader):
					edge = graph.add_edge(nodes[current_row['name']]['Index'],nodes[next_row['name']]['Index'])
					lon1 = float(mrts[current_row['name']]['Longitude'])
					lat1 = float(mrts[current_row['name']]['Latitude'])
					lon2 = float(mrts[next_row['name']]['Longitude'])
					lat2 = float(mrts[current_row['name']]['Latitude'])
					dist = round(haversine(lon1, lat1, lon2, lat2),3)
					
					graph.ep.Distance[edge] = dist
					graph.ep.Method[edge] = 'MRT'
					
					#current_name = next_station['Node'] + ' ' + line + ' 2'
					#next_name = current_station['Node'] + ' ' + line + ' 2'
					edge = graph.add_edge(nodes[next_row['name']]['Index'],nodes[current_row['name']]['Index'])
					graph.ep.Distance[edge] = dist
					graph.ep.Method[edge] = 'MRT'


	os.chdir('..')
	if temp == "EW":
		edge = graph.add_edge(nodes['Expo CG']['Index'],nodes['Tanah Merah EW']['Index'])
		lon1 = float(nodes['Expo CG']['Longitude'])
		lat1 = float(nodes['Expo CG']['Latitude'])
		lon2 = float(nodes['Tanah Merah EW']['Longitude'])
		lat2 = float(nodes['Tanah Merah EW']['Latitude'])
		dist = round(haversine(lon1, lat1, lon2, lat2),3)
		graph.ep.Distance[edge] = dist
		graph.ep.Method[edge] = 'MRT'
		edge = graph.add_edge(nodes['Tanah Merah EW']['Index'],nodes['Expo CG']['Index'])
		graph.ep.Distance[edge] = dist
		graph.ep.Method[edge] = 'MRT'

	if temp == "CC":
		edge = graph.add_edge(nodes['Bayfront CE']['Index'],nodes['Promenade CC']['Index'])
		lon1 = float(nodes['Bayfront CE']['Longitude'])
		lat1 = float(nodes['Bayfront CE']['Latitude'])
		lon2 = float(nodes['Promenade CC']['Longitude'])
		lat2 = float(nodes['Promenade CC']['Latitude'])
		dist = round(haversine(lon1, lat1, lon2, lat2),3)
		graph.ep.Distance[edge] = dist
		graph.ep.Method[edge] = 'MRT'
		edge = graph.add_edge(nodes['Promenade CC']['Index'],nodes['Bayfront CE']['Index'])
		graph.ep.Distance[edge] = dist
		graph.ep.Method[edge] = 'MRT'



	for e in graph.edges():
		graph.ep.Time[e] = 2

	if temp == "NS":
		edge = graph.edge(nodes['Jurong East NS']['Index'],nodes['Bukit Batok NS']['Index'])
		graph.ep.Time[edge] = 3
		edge = graph.edge(nodes['Bukit Batok NS']['Index'],nodes['Jurong East NS']['Index'])
		graph.ep.Time[edge] = 3

		edge = graph.edge(nodes['Bukit Gombak NS']['Index'],nodes['Choa Chu Kang NS']['Index'])
		graph.ep.Time[edge] = 3
		edge = graph.edge(nodes['Choa Chu Kang NS']['Index'],nodes['Bukit Gombak NS']['Index'])
		graph.ep.Time[edge] = 3

		edge = graph.edge(nodes['Yew Tee NS']['Index'],nodes['Kranji NS']['Index'])
		graph.ep.Time[edge] = 4
		edge = graph.edge(nodes['Kranji NS']['Index'],nodes['Yew Tee NS']['Index'])
		graph.ep.Time[edge] = 4

		edge = graph.edge(nodes['Admiralty NS']['Index'],nodes['Sembawang NS']['Index'])
		graph.ep.Time[edge] = 5
		edge = graph.edge(nodes['Sembawang NS']['Index'],nodes['Admiralty NS']['Index'])
		graph.ep.Time[edge] = 5

		edge = graph.edge(nodes['Khatib NS']['Index'],nodes['Yio Chu Kang NS']['Index'])
		graph.ep.Time[edge] = 5
		edge = graph.edge(nodes['Yio Chu Kang NS']['Index'],nodes['Khatib NS']['Index'])
		graph.ep.Time[edge] = 5

		edge = graph.edge(nodes['Ang Mo Kio NS']['Index'],nodes['Bishan NS']['Index'])
		graph.ep.Time[edge] = 3
		edge = graph.edge(nodes['Bishan NS']['Index'],nodes['Ang Mo Kio NS']['Index'])
		graph.ep.Time[edge] = 3

		edge = graph.edge(nodes['Somerset NS']['Index'],nodes['Dhoby Ghaut NS']['Index'])
		graph.ep.Time[edge] = 1
		edge = graph.edge(nodes['Dhoby Ghaut NS']['Index'],nodes['Somerset NS']['Index'])
		graph.ep.Time[edge] = 1

	elif temp == "CC":
		edge = graph.edge(nodes['Bartley CC']['Index'],nodes['Serangoon CC']['Index'])
		graph.ep.Time[edge] = 3
		edge = graph.edge(nodes['Serangoon CC']['Index'],nodes['Bartley CC']['Index'])
		graph.ep.Time[edge] = 3

		edge = graph.edge(nodes['Bishan CC']['Index'],nodes['Marymount CC']['Index'])
		graph.ep.Time[edge] = 3
		edge = graph.edge(nodes['Marymount CC']['Index'],nodes['Bishan CC']['Index'])
		graph.ep.Time[edge] = 3

		edge = graph.edge(nodes['Botanic Gardens CC']['Index'],nodes['Caldecott CC']['Index'])
		graph.ep.Time[edge] = 5
		edge = graph.edge(nodes['Caldecott CC']['Index'],nodes['Botanic Gardens CC']['Index'])
		graph.ep.Time[edge] = 5

		edge = graph.edge(nodes['Farrer Road CC']['Index'],nodes['Holland Village CC']['Index'])
		graph.ep.Time[edge] = 3
		edge = graph.edge(nodes['Holland Village CC']['Index'],nodes['Farrer Road CC']['Index'])
		graph.ep.Time[edge] = 3

		edge = graph.edge(nodes['Pasir Panjang CC']['Index'],nodes['Labrador Park CC']['Index'])
		graph.ep.Time[edge] = 3
		edge = graph.edge(nodes['Labrador Park CC']['Index'],nodes['Pasir Panjang CC']['Index'])
		graph.ep.Time[edge] = 3

		edge = graph.edge(nodes['Bayfront CE']['Index'],nodes['Marina Bay CE']['Index'])
		graph.ep.Time[edge] = 3
		edge = graph.edge(nodes['Marina Bay CE']['Index'],nodes['Bayfront CE']['Index'])
		graph.ep.Time[edge] = 3

	elif temp == "NE":
		edge = graph.edge(nodes['HarbourFront NE']['Index'],nodes['Outram Park NE']['Index'])
		graph.ep.Time[edge] = 3
		edge = graph.edge(nodes['Outram Park NE']['Index'],nodes['HarbourFront NE']['Index'])
		graph.ep.Time[edge] = 3

		edge = graph.edge(nodes['Serangoon NE']['Index'],nodes['Kovan NE']['Index'])
		graph.ep.Time[edge] = 3
		edge = graph.edge(nodes['Kovan NE']['Index'],nodes['Serangoon NE']['Index'])
		graph.ep.Time[edge] = 3

		edge = graph.edge(nodes['Hougang NE']['Index'],nodes['Buangkok NE']['Index'])
		graph.ep.Time[edge] = 3
		edge = graph.edge(nodes['Buangkok NE']['Index'],nodes['Hougang NE']['Index'])
		graph.ep.Time[edge] = 3

		edge = graph.edge(nodes['Sengkang NE']['Index'],nodes['Punggol NE']['Index'])
		graph.ep.Time[edge] = 3
		edge = graph.edge(nodes['Punggol NE']['Index'],nodes['Sengkang NE']['Index'])
		graph.ep.Time[edge] = 3

	elif temp == "EW":
		edge = graph.edge(nodes['Pasir Ris EW']['Index'],nodes['Tampines EW']['Index'])
		graph.ep.Time[edge] = 3
		edge = graph.edge(nodes['Tampines EW']['Index'],nodes['Pasir Ris EW']['Index'])
		graph.ep.Time[edge] = 3

		edge = graph.edge(nodes['Simei EW']['Index'],nodes['Tanah Merah EW']['Index'])
		graph.ep.Time[edge] = 3
		edge = graph.edge(nodes['Tanah Merah EW']['Index'],nodes['Simei EW']['Index'])
		graph.ep.Time[edge] = 3

		edge = graph.edge(nodes['Clementi EW']['Index'],nodes['Jurong East EW']['Index'])
		graph.ep.Time[edge] = 4
		edge = graph.edge(nodes['Jurong East EW']['Index'],nodes['Clementi EW']['Index'])
		graph.ep.Time[edge] = 4

		edge = graph.edge(nodes['Tanah Merah EW']['Index'],nodes['Expo CG']['Index'])
		graph.ep.Time[edge] = 4
		edge = graph.edge(nodes['Expo CG']['Index'],nodes['Tanah Merah EW']['Index'])
		graph.ep.Time[edge] = 4

		edge = graph.edge(nodes['Changi Airport CG']['Index'],nodes['Expo CG']['Index'])
		graph.ep.Time[edge] = 9
		edge = graph.edge(nodes['Expo CG']['Index'],nodes['Changi Airport CG']['Index'])
		graph.ep.Time[edge] = 9


	return graph

"""
----------------------------------------------------------------------------------------------------
"""	
"""
-----------------------------Initialize Graph--------------------------
"""
def init_graph():
	global bus_stops, mrts, nodes, posts
	graph = Graph()
	graph.vp.name = graph.new_vertex_property('string')
	graph.vp.Type = graph.new_vertex_property('string')
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
		graph.vp.Type[index] = nodes[item]['Type']
		graph.vp.Location[index] = nodes[item]['Location']
		graph.vp.Latitude[index] = nodes[item]['Latitude']
		graph.vp.Longitude[index] = nodes[item]['Longitude']
		i += 1
	graph.ep.Method = graph.new_edge_property('string')
	graph.ep.Distance = graph.new_edge_property('float')
	graph.ep.Time = graph.new_edge_property('int')

	return graph
"""
----------------------------------------------------------------------------------------------------
"""		
"""
-----------------------------Connect Post Codes to Bus stops and MRT--------------------------
"""	
def connect_post_code(graph):
	global posts, bus_stops, mrts, nodes

	for item in posts:
		lat1 = float(posts[item]['Latitude'])
		lon1 = float(posts[item]['Longitude'])
		connected = 0
		min_dist = 10
		for stop in bus_stops:
			lat2 = float(bus_stops[stop]['Latitude'])
			lon2 = float(bus_stops[stop]['Longitude'])
			dist = round(haversine(lon1,lat1,lon2,lat2),3)
			if dist < 0.2:
				edge = graph.add_edge(nodes[item]['Index'],nodes[stop]['Index'])
				graph.ep.Distance[edge] = dist * 1.5
				graph.ep.Method[edge] = 'Walking'
				graph.ep.Time[edge] = round(dist/5*60,3)
				edge = graph.add_edge(nodes[stop]['Index'],nodes[item]['Index'])
				graph.ep.Distance[edge] = dist * 1.5
				graph.ep.Method[edge] = 'Walking'
				graph.ep.Time[edge] = round(dist/5*60,3)
				connected += 1
			elif dist < min_dist:
				min_dist = dist
				min_stn = stop
		for mrt in mrts:
			lat2 = float(mrts[mrt]['Latitude'])
			lon2 = float(mrts[mrt]['Longitude'])
			dist = round(haversine(lon1,lat1,lon2,lat2),3)
			if dist < 0.2:
				edge = graph.add_edge(nodes[item]['Index'],nodes[mrt]['Index'])
				graph.ep.Distance[edge] = dist * 1.5
				graph.ep.Method[edge] = 'Walking'
				graph.ep.Time[edge] = round(dist*1.5/5*60,3)
				edge = graph.add_edge(nodes[mrt]['Index'],nodes[item]['Index'])
				graph.ep.Distance[edge] = dist * 1.5
				graph.ep.Method[edge] = 'Walking'
				graph.ep.Time[edge] = round(dist*1.5/5*60,3)
				connected += 1
			elif dist < min_dist:
				min_dist = dist
				min_stn = mrt
		if connected == 0:
				edge = graph.add_edge(nodes[item]['Index'],nodes[min_stn]['Index'])
				graph.ep.Distance[edge] = min_dist * 1.5
				graph.ep.Method[edge] = 'Walking'
				graph.ep.Time[edge] = round(min_dist*1.5/5*60,3)
				edge = graph.add_edge(nodes[min_stn]['Index'],nodes[item]['Index'])
				graph.ep.Distance[edge] = min_dist * 1.5
				graph.ep.Method[edge] = 'Walking'
				graph.ep.Time[edge] = round(min_dist*1.5/5*60,3)

	return graph
"""
----------------------------------------------------------------------------------------------------
"""	

if __name__ == '__main__':
	temp = str(sys.argv[1])
	unknown =read_bus_stop_file('info.csv')
	#print sorted(lines['NS'],key=lambda k: k['Location'])
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
	graph = connect_MRT(graph,temp)
	os.chdir('./SBST')
	for file_name in os.listdir(os.getcwd()):
		if file_name.endswith('.csv'):
			graph = read_route_file(file_name, graph)
	os.chdir('../SMRT')
	for file_name in os.listdir(os.getcwd()):
		if file_name.endswith('.csv'):
			graph = read_route_file(file_name, graph)
	os.chdir('../')

	
	graph = connect_bus_MRT(graph)
	graph = connect_post_code(graph)
	os.chdir('./all_results')
	saved_name = temp + "_graph.graphml"
	graph.save(saved_name)
