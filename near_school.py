from itertools import tee, izip
import csv
import xml.etree.cElementTree as ET
import os, sys
from collections import defaultdict
from math import radians, cos, sin, asin, sqrt
import operator
from operator import itemgetter
import MySQLdb

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

def init_db():
	db = MySQLdb.connect(host="localhost",    # your host, usually localhost
	user="root",         # your username
	passwd="LZXihpc12",  # your password
	db="HDBPrice")        # name of the data base
	return db

def add_school(db):
	cur1 = db.cursor()
	cur2 = db.cursor()
	command1 = 'SELECT h.postcode, p.lon, p.lat FROM hdb h, postcode p WHERE h.postcode = p.name'
	command2 = 'SELECT s.name, p.lon, p.lat FROM school s, postcode p '
	command2 = command2 + 'WHERE s.postcode = p.name'
	cur1.execute(command1)
	for row in cur1.fetchall():
		dists = list()
		lon1 = row[1]
		lat1 = row[2]
		#print lon1, ' ', lat1
		cur2.execute(command2)
		pc = row[0]
		for row in cur2.fetchall():
			#print row
			lon2 = row[1]
			lat2 = row[2]
			#print lon2, ' ', lat2
			dist = haversine(lon1, lat1, lon2, lat2)
			mall = dict()
			mall['name'] = row[0]
			mall['dist'] = dist
			#print mall
			dists.append(mall)
		st = sorted(dists, key=itemgetter('dist'))
		command3 = 'INSERT INTO nearschool (postcode,school1,dist1,school2,dist2,school3,dist3) VALUES ('
		command3 = command3 + str(pc) + ',"' + st[0]['name'] + '",' + str(st[0]['dist']) + ',"' + st[1]['name'] + '",' + str(st[1]['dist']) + ',"' + st[2]['name'] + '",' + str(st[2]['dist']) + ')'
		try:
			cur = db.cursor()
			cur.execute(command3)
			db.commit()
		except:
			db.rollback()


if __name__ == '__main__':

    db = init_db()
    #os.chdir('./HDBPriceFor2013')
    add_school(db)
    db.close()
