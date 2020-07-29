# -*- coding: utf-8 -*-
import csv
import logging
import codecs

def write_csv(fn,data,encode='utf-8'):
	path = 'db/'+fn
	with codecs.open(path,'w', encoding=encode) as csvFile:
		writef = csv.writer(csvFile, delimiter=';')
		writef.writerows(data)
	logging.info('File created successfully - %s'%path)
	csvFile.close()

def write_add_csv(fn,data):
	path = 'db/'+fn
	with codecs.open(path,'a', encoding='utf-8') as csvFile:
		writef = csv.writer(csvFile, delimiter=';')
		writef.writerows(data)
	logging.info('File created successfully - %s'%path)
	csvFile.close()

def write_for_sheets(fn,data,book):
	path = 'db/'+fn
	with codecs.open(path,'w', encoding='utf-8') as csvFile:
		for i in range(0,len(data)):
			writef = csv.writer(csvFile, delimiter=';')
			writef.writerow(data[i])
			writef.writerow(book[i])
	logging.info('File created successfully - %s'%path)

def read_csv(fn,encode='utf-8'):
	data = []
	path = 'db/'+fn
	with codecs.open(path,'r', encoding=encode) as csvFile:
		readf = csv.reader(csvFile, delimiter=';')
		try:
			data = list(readf)
			#for row in readf:
			#	data.append(tuple(row))
			logging.info('File read successfully - %s'%path)
		except csv.Error:
			logging.info('File reading error - %s'%path)
	csvFile.close()
	return data
