
from itertools import tee, izip
import csv
import xml.etree.cElementTree as ET
import os, sys
from collections import defaultdict
from math import radians, cos, sin, asin, sqrt
import operator


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
		for row in reader:
			
			if row['Node'].isdigit() and len(row['Node']) == 4:
				row['Node'] = '0' + row['Node']
			if row['Node'].isdigit():
				bus_stops[row['Node']] = dict()
				bus_stops[row['Node']]['Location'] = row['Info1']
				bus_stops[row['Node']]['Longitude'] = row['Long']
				bus_stops[row['Node']]['Latitude'] = row['Lat']
			if row['Node'].isdigit() == False:
				mrt_code = list()
				mrt_code = row['Info1'].split('/')
				for item in mrt_code:
						lines[item[:2]].append(row)
		
			
"""
----------------------------------------------------------------------------------------------------
"""


"""
------------------------------------add bus services as edges-----------------------------------------
"""
def read_route_file(filename, g):
	global services
	with open (filename) as route:
		reader = csv.DictReader(route,fieldnames=['1','stop_no','distance','express','arr_time','dep_time','last_bus','ID','direction','service_no'])
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






if __name__ == '__main__':
	
	read_bus_stop_file('info.csv')
	#print sorted(lines['NS'],key=lambda k: k['Location'])
	unknown = find_unknown_node()
	print unknown
	add_unknown_node(unknown)

