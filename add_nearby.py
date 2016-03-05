from itertools import tee, izip
import csv
import xml.etree.cElementTree as ET
import os, sys
from collections import defaultdict
from math import radians, cos, sin, asin, sqrt
import operator
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

def add_mall(db):
	dists = defaultdict(list)
	cur1 = db.cursor()
	cur2 = db.cursor()
	command1 = 'SELECT h.postcode, p.lon, p.lat FROM hdb h, postcode p WHERE h.postcode = p.name'
	command2 = 'SELECT m.name, m.postcode, p.lon, p.lat FROM mall m, postcode p '
	command2 = command1 + 'WHERE m.postcode = p.name'
	cur1.execute(command1)
	for row in cur1.fetchall():
		lon1 = row[1]
		lat1 = row[2]
		cur2.execute(command2)
		for row in cur2.fetchall():
			lon2 = row[1]
			lat2 = row[2]
			dist = haversine(lon1, lat1, lon2, lat2)
			dists[row[0]] = dist
		print dists


	for row in cur.fetchall():
		print row

if __name__ == '__main__':

    db = init_db()
    #os.chdir('./HDBPriceFor2013')
    add_mall(db)
    db.close()
