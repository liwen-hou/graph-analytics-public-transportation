from itertools import tee, izip
import csv
import xml.etree.cElementTree as ET
import os, sys
from collections import defaultdict
from math import radians, cos, sin, asin, sqrt
import operator
from operator import itemgetter
import MySQLdb

def init_db():
	db = MySQLdb.connect(host="localhost",    # your host, usually localhost
	user="root",         # your username
	passwd="LZXihpc12",  # your password
	db="HDBPrice")        # name of the data base
	return db

def combine(db):

	cur = db.cursor()
	command = 'SELECT count(*) '#h.postcode, p.lon, p.lat, h.block, h.floor, h.age, h.size, h.price, h.rooms, p.clt, p.cld, p.clg,mt.mrt1, mt.dist1, mt.mrt2, mt.dist2, mt.mrt3, mt.dist3, sh.school1, sh.dist1, sh.school2, sh.dist2, sh.school3, sh.dist3, ml.mall1, ml.dist1, ml.mall2, ml.dist2, ml.mall3, ml.dist3 '
	command = command + 'FROM hdb h, postcode p, nearschool sh, nearmrt mt, nearmall ml '
	command = command + 'WHERE h.postcode = p.name AND h.postcode = sh.postcode AND h.postcode = ml.postcode AND h.postcode = mt.postcode'




if __name__ == '__main__':

    db = init_db()
    #os.chdir('./HDBPriceFor2013')
    add_school(db)
    db.close()
