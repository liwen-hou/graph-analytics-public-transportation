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

def find_postcode(filename, db):
    cur = db.cursor()
    with open(filename) as hdb:
        reader = csv.DictReader(hdb,fieldnames = ['id','date','addr','type','year','age','floor','size','price','psf','rooms','lat','lon'])
        next(reader,None)
        for row in reader:
            addr = row['addr'].split(' ')
            tail = addr[0]
            if tail.isdigit():
                if len(tail) != 3:
                    for i in range(0,3-len(tail)):
                        tail = '0' + tail
            else:
                tail = tail[:-1]
                if len(tail) != 3:
                    for i in range(0,3-len(tail)):
                        tail = '0' + tail
            command = 'SELECT * FROM address ' + 'WHERE postcode LIKE "%' + tail + '"'
            cur.execute(command)
            for result in cur.fetchall():
                temp = result[0].split(',')
                if len(addr) > 2:
                    if (addr[2] in temp[0].upper() and addr[1] in temp[0].upper()) or (addr[2] in temp[1].upper() and addr[1] in temp[1].upper()):
                        if addr[0] == temp[1][1:] or addr[0] == temp[2][1:]:
                            pc = result[1]
                            print pc
                else:
                    if (addr[1] in temp[0].upper()) or (addr[1] in temp[1].upper()):
                        if addr[0] == temp[1][1:] or addr[0] == temp[2][1:]:
                            pc = result[1]
                            print pc
            flr = row['floor'].split(' ')
            flr = (int(flr[0]) + int(flr[2]))/2
            command = 'INSERT INTO hdb (floor,age,size,price,rooms,block,postcode) VALUES ('
            command = command + str(flr) + ',' + row['age'] + ',' + row['size'] + ',' + row['price'] + ',' + row['rooms'] + ',"' + row['addr'] + '",' + str(pc) + ')'
            # try:
            #     cur.execute(command)
            #     db.commit()
            # except:
            #     db.rollback()
if __name__ == '__main__':

    db = init_db()
    os.chdir('./HDBPriceFor2013')
    find_postcode('Queenstown_done.csv',db)
    # for file_name in os.listdir(os.getcwd()):
    #     if file_name.endswith('.csv'):
    #         find_postcode(file_name, db)
    db.close()
