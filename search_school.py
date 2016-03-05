
from itertools import tee, izip
import csv
import xml.etree.cElementTree as ET
import os, sys
from collections import defaultdict
import operator


def search_school():

	osm_file = open('singapore.osm', "r")
	schools = list()
	for event, elem in ET.iterparse(osm_file, events=("start",)):
		school = dict()		
		if elem.tag == "way":
			for tag in elem.iter("tag"):
				if tag.attrib['k'] == 'amenity' and tag.attrib['v'] == 'school' or tag.attrib['v'] == 'university':
					school['type'] = tag.attrib['v']
				elif tag.attrib['k'] == 'addr:postcode':
					school['postcode'] = tag.attrib['v']
				elif tag.attrib['k'] == 'name':
					school['name'] = tag.attrib['v']
			if len(school) == 3:
				#print school
				schools.append(school)
	schools.remove({'type': 'school', 'name': u'Child Development Centre \u2013 Bukit Batok', 'postcode': '659759'})
	for school in schools:
		print school
		with open('school.csv','ab') as result:
			writer = csv.writer(result,delimiter = ',')
			writer.writerow([school['name'],school['postcode']])

if __name__ == '__main__':

	search_school()