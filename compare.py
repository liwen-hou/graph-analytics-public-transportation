from itertools import tee, izip
import csv
import os, sys
from collections import defaultdict
from math import radians, cos, sin, asin, sqrt
import operator

def compare():
	changes = defaultdict(list)
	with open('extracted_no_mrt.csv') as no_mrt, open('extracted_with_mrt.csv') as with_mrt:
		reader1 = csv.DictReader(no_mrt,fieldnames = ['name','lon','lat','mrt','cl','dist'])
		reader2 = csv.DictReader(with_mrt,fieldnames = ['name','lon','lat','mrt','cl','dist'])
		for row1, row2 in izip(reader1,reader2):
			if row1['name'] != row2['name']:
				print 'terminated'
				return
			changes[row1['mrt']] = list()
			change = (float(row2['cl']) - float(row1['cl']))/float(row1['dist'])
			changes[row1['mrt']].append(change)
	return changes

if __name__ == '__main__':
	changes = compare()
	print changes