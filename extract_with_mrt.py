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
-----------------------------Read Bus Stop Files and add bus stops as nodes--------------------------
"""
def read_bus_stop_file(filename):
	global lines
	with open (filename) as stop_file:
		reader = csv.DictReader(stop_file)
		all_stops = defaultdict(list)
		for row in reader:
			
			if row['Node'].isdigit() == False:
				mrt_code = list()
				mrt_code = row['Info1'].split('/')
				for item in mrt_code:
						lines[item[:2]].append(row)

		
			
"""
----------------------------------------------------------------------------------------------------
"""


"""
------------------------------------add MRT stations as nodes-----------------------------------------
"""
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

	mrts['Punggol PTC'] = dict()
	mrts['Punggol PTC']['Location'] = 'PTC'
	mrts['Punggol PTC']["Longitude"] = mrts['Punggol NE']["Longitude"]
	mrts['Punggol PTC']["Latitude"] = mrts['Punggol NE']["Latitude"] 

	mrts['Sengkang STC'] = dict()
	mrts['Sengkang STC']['Location'] = 'STC'
	mrts['Sengkang STC']["Longitude"] = mrts['Sengkang NE']["Longitude"]
	mrts['Sengkang STC']["Latitude"] = mrts['Sengkang NE']["Latitude"]
	
"""
----------------------------------------------------------------------------------------------------
"""




if __name__ == '__main__':
	
	read_bus_stop_file('info.csv')
	#print sorted(lines['NS'],key=lambda k: k['Location'])
	#add_unknown_node(unknown)
	add_MRT()
	# os.chdir('./ZXPostCode')
	# for file_name in os.listdir(os.getcwd()):
	# 	if file_name.endswith('.csv'):
	# 		add_post_code(file_name)
	# os.chdir('../')
	os.chdir('./all_results')
	with open ('results_time.csv') as result:
		reader = csv.DictReader(result)
		for row in reader:
			if row['Type'] == 'Post Code':
				lon = float(row['Longitude'])
				lat = float(row['Latitude'])
				for mrt in mrts:
					lon2 = float(mrts[mrt]['Longitude'])
					lat2 = float(mrts[mrt]['Latitude'])
					dist = haversine(lon, lat, lon2, lat2)
					if dist < .5:
						with open('extracted_with_mrt.csv','ab') as new_result:
							writer = csv.writer(new_result,delimiter=',')
							writer.writerow([row['Name'],row['Longitude'],row['Latitude'],mrt,row['Closeness_Time'],dist])


	#delete empty stops
	# delete_stop = list()
	# for stop in bus_stops:
	# 	if not bus_stops[stop]:
	# 		delete_stop.append(stop)
	# for stop in delete_stop:
	# 	del bus_stops[stop]


	

	# os.chdir('./SBST')
	# for file_name in os.listdir(os.getcwd()):
	# 	if file_name.endswith('.csv'):
	# 		graph = read_route_file(file_name, graph)
	# os.chdir('../SMRT')
	# for file_name in os.listdir(os.getcwd()):
	# 	if file_name.endswith('.csv'):
	# 		graph = read_route_file(file_name, graph)
	# os.chdir('../')

	
	# graph = connect_MRT(graph)
	# graph = connect_bus_MRT(graph)
	# graph = connect_post_code(graph)

	# graph.save('sg_graph.graphml')

	# calculate_centrality(graph)
