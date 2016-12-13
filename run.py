#!/usr/bin/python
#-*- coding: utf-8 -*-

import sys
import os
from terminaltables import AsciiTable,SingleTable
from colorclass import Color, Windows
from JSMTrace.database import JSMT_DB

mTypeTable = {'m':'alloc','f':'free','u':"access",'l':'load','s':'store'}

def main(argv):
	global groupByJsAlloc
	global groupByJsLine

	db = JSMT_DB()

	jsFP = open(argv[0],"rb+")
	js_content = jsFP.read()

	task_id = db.add_task(argv[0],js_content)
	if not task_id :
		raise NameError('[+] JSMTrace Run.py Exception : add task fail.')

	os.system("v8/out/Release/d8 --expose-gc %s 2> %s"%(argv[0],argv[1]))

	result = db.set_task_state(task_id,"running")
	if not result:
		raise NameError('[+] JSMTrace Run.py Exception : set task fail.')

	inFP = open(argv[1],"rb+")
	outFP = open(argv[2],"wb+")

	logLines = inFP.readlines()
	# memoryTable = {}

	jsLineInfos = {}
	contextTable = {}
	contextId = 0

	groupByJsAlloc = {}
	groupByJsLine = {}

	contextTable[0] = ['unknown','?','?','?']
	contextTable[-1] = ['unknown','?','?','?']
	# memoryTable['-1'] = -1
	# memoryTable['0'] = 0
	for line in logLines:
		# outFP.write(line)
		line = line.strip('\r\n') 

		if line.startswith('[R') :
			# print "Runtime Trace"
			rtInfo = line.split(":")[1]
			fName,lineNum,colNum = rtInfo.split("#")

			contextId += 1
			contextTable[contextId] = [fName,lineNum,colNum]

		elif line.startswith('[m') :
			# print "malloc"
			mInfo	= line[4:].split(",")
			mId		= mInfo[2]
			# memoryTable[mId] = contextId
			# memoryTable[mId] = [fName,lineNum,colNum]

			if not argv[0] in fName:
				continue

			fName,lineNum,colNum = contextTable[contextId]

			if len(mInfo) == 6:	
				Address,Size,mId,stackSize,stackAddress,mIdValue = mInfo

				log_id = db.add_log(task_id,lineNum,colNum,mId,contextId,Size,Address,'alloc',stackSize,stackAddress)
				if not log_id :
					raise NameError('[+] JSMTrace Run.py Exception : add log fail.')

			elif len(mInfo) == 4:
				raise NameError('[+] JSMTrace Run.py Exception : mInfo size Error !')		
			else :
				raise NameError('[+] JSMTrace Run.py Exception : mInfo size Error !')		


		elif line.startswith('[f') :
			mInfo	= line[4:].split(",")
			mId		= mInfo[2]


			if not argv[0] in fName:
				continue

			fName,lineNum,colNum = contextTable[contextId]

			if len(mInfo) == 6:	
				Address,Size,mId,stackSize,stackAddress,mIdValue = mInfo

				log_id = db.add_log(task_id,lineNum,colNum,mId,contextId,Size,Address,'free',stackSize,stackAddress)
				if not log_id :
					raise NameError('[+] JSMTrace Run.py Exception : add log fail.')

			elif len(mInfo) == 4:
				raise NameError('[+] JSMTrace Run.py Exception : mInfo size Error !')		
			else :
				raise NameError('[+] JSMTrace Run.py Exception : mInfo size Error !')		

		elif line.startswith('[u') :
			mInfo	= line[4:].split(",")
			mId		= mInfo[2]


			if not argv[0] in fName:
				continue

			fName,lineNum,colNum = contextTable[contextId]

			if len(mInfo) == 6:	
				raise NameError('[+] JSMTrace Run.py Exception : mInfo size Error !')		
			elif len(mInfo) == 4:

				Address,Size,mId,accessType = mInfo

				log_id = db.add_log(task_id,lineNum,colNum,mId,contextId,Size,Address,accessType,'','')
				if not log_id :
					raise NameError('[+] JSMTrace Run.py Exception : add log fail.')
			else :
				raise NameError('[+] JSMTrace Run.py Exception : mInfo size Error !')		

	task_id = db.set_task_state(task_id,"success")
	if not task_id :
		raise NameError('[+] JSMTrace Run.py Exception : set task fail.')



if __name__ == "__main__":
	if(len(sys.argv)!=4):
		print "run.py array_test.js out.log sOut.log"
	
	main(sys.argv[1:])
