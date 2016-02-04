
from itertools import tee, izip
import csv
import xml.etree.cElementTree as ET
import os, sys
from collections import defaultdict
from math import radians, cos, sin, asin, sqrt
import operator

if __name__ == '__main__':
	
	os.chdir('./SBST')
	for file_name in os.listdir(os.getcwd()):
		if file_name.endswith('.csv'):
			print file_name
			with open(file_name) as route:
				reader = csv.DictReader(route,fieldnames=['1','stop_no','distance','express','first_bus','dep_time','last_bus','ID','direction','service_no'])
				for row in reader:
					print row['stop_no']
					if row['stop_no'] == '49229':
						print 'true'
	os.chdir('../SMRT')
	for file_name in os.listdir(os.getcwd()):
		if file_name.endswith('.csv'):
			print file_name
			with open(file_name) as route:
				reader = csv.DictReader(route,fieldnames=['1','stop_no','distance','express','first_bus','dep_time','last_bus','ID','direction','service_no'])
				for row in reader:
					print row['stop_no']
					if row['stop_no'] == '49229':
						print 'true'
	os.chdir('../')
