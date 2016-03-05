import csv
import os, sys
import operator
import MySQLdb

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
            row['addr'] = row['addr'].replace("C'WEALTH",'COMMON WEALTH')
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
                else:
                    if (addr[1] in temp[0].upper()) or (addr[1] in temp[1].upper()):
                        if addr[0] == temp[1][1:] or addr[0] == temp[2][1:]:
                            pc = result[1]
            flr = row['floor'].split(' ')
            flr = (int(flr[0]) + int(flr[2]))/2
            command = 'INSERT INTO hdb (floor,age,size,price,rooms,block,postcode) VALUES ('
            command = command + str(flr) + ',' + row['age'] + ',' + row['size'] + ',' + row['price'] + ',' + row['rooms'] + ',"' + row['addr'] + '",' + str(pc) + ')'
            try:
                cur.execute(command)
                db.commit()
            except:
                db.rollback()
if __name__ == '__main__':

    db = init_db()
    os.chdir('./HDBPriceFor2013')
    for file_name in os.listdir(os.getcwd()):
        if file_name.endswith('.csv'):
            print file_name
            find_postcode(file_name, db)
    db.close()
