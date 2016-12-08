#!/usr/bin/python
import sys
import os
from terminaltables import AsciiTable,SingleTable
from colorclass import Color, Windows

mTypeTable = {'m':'alloc','f':'free','u':"access",'l':'load','s':'store'}

def appendLog(fName,lineNum,colNum,codeLine,mInfo,mId,aType):
	global groupByJsAlloc
	global groupByJsLine

	if not groupByJsLine.has_key(fName):
		groupByJsLine[fName] = {}

	if not groupByJsLine[fName].has_key(lineNum):
		groupByJsLine[fName][lineNum] = {}

	if not groupByJsLine[fName][lineNum].has_key(mId):
		groupByJsLine[fName][lineNum][mId] = {}

	if not groupByJsLine[fName][lineNum][mId].has_key(aType):
		groupByJsLine[fName][lineNum][mId][aType] = []

	# [m] 62d000762400,33264,101,26,7f7195b6d88a,-1,
	Type = mTypeTable[aType]
	if len(mInfo) == 6:	
		Address,Size,mId,stackSize,stackAddress,mIdValue = mInfo
		groupByJsLine[fName][lineNum][mId][aType].append([Type,Address,Size,mId,stackSize,stackAddress,mIdValue,"",""])
	elif len(mInfo) == 4:
		Address,Size,mId,accessType = mInfo
		groupByJsLine[fName][lineNum][mId][aType].append([accessType,Address,Size,mId,"","","","",""])
	else :
		raise NameError('mInfo size Error !')		

	if not groupByJsAlloc.has_key(fName):
		groupByJsAlloc[fName] = {mId:{}}

	if not groupByJsAlloc[fName].has_key(mId):
		groupByJsAlloc[fName][mId] = {}

	if not groupByJsAlloc[fName][mId].has_key(aType):
		groupByJsAlloc[fName][mId][aType] = []

	Type = mTypeTable[aType]
	if len(mInfo) == 6:	
		Address,Size,mId,stackSize,stackAddress,mIdValue = mInfo
		# groupByJsLine[fName][lineNum][mId][aType].append([Type,Address,Size,mId,stackSize,stackAddress,mIdValue])
		groupByJsAlloc[fName][mId][aType].append([Type,Address,Size,mId,stackSize,stackAddress,mIdValue,codeLine,"%s#%s"%(lineNum,colNum)])
	elif len(mInfo) == 4:
		Address,Size,mId,accessType = mInfo
		# groupByJsLine[fName][lineNum][mId][aType].append([Type,Address,Size,mId,accessType])
		groupByJsAlloc[fName][mId][aType].append([accessType,Address,Size,mId,"","","",codeLine,"%s#%s"%(lineNum,colNum)])
	else :
		raise NameError('mInfo size Error !')		

	# groupByJsAlloc[fName][mId][aType].append("%s, %s, #%s#%s"%(mInfo,codeLine,lineNum,colNum))
	

def filterLog():
	global groupByJsAlloc
	global groupByJsLine

	delList = []

	for fName in groupByJsLine:
		# print fName
		if fName in ['native test-extra.js','unknown']:
			groupByJsLine[fName]={}
			groupByJsAlloc[fName]={}

	for fName in groupByJsLine:
		for lineNum in groupByJsLine[fName]:
			for mId in groupByJsLine[fName][lineNum]:
				if groupByJsLine[fName][lineNum][mId].has_key('m') and groupByJsLine[fName][lineNum][mId].has_key('f'):
					a = 1
					groupByJsLine[fName][lineNum][mId]={}
					groupByJsAlloc[fName][mId]={}

def printLog():
	global groupByJsAlloc
	global groupByJsLine
	# fprintf(stderr,"[m] %llx,%d,%d,%d,%llx,%d\n",addr,size,__asan_mallocId,stack->size,stack->trace_buffer[i],midValue);

	print "---------------------------------"
	print " group By Js Line"
	print "---------------------------------"

	for fName in groupByJsLine:
		for lineNum in groupByJsLine[fName]:
			for mId in groupByJsLine[fName][lineNum]:
				# for aType in groupByJsLine[fName][lineNum][mId]:
					# for line in groupByJsLine[fName][lineNum][mId][aType]:
					# 	print line
				if groupByJsLine[fName][lineNum][mId].has_key('m'):
					for line in groupByJsLine[fName][lineNum][mId]['m']:
						print "%s"%(line)

				if groupByJsLine[fName][lineNum][mId].has_key('f'):
					for line in groupByJsLine[fName][lineNum][mId]['f']:
						print "%s"%(line)


		if os.path.isfile(fName):
			jsFP = open(fName,"rb+")
			jsLines = jsFP.readlines()
			jsFP.close()

			filename, file_extension = os.path.splitext(fName)
			print filename, file_extension
			jsOutFP = open("%s_mtrace.%s"%(filename,'js'),"wb+")

			for lineIdx in range(len(jsLines)):
				jsOutFP.write(jsLines[lineIdx])
				if groupByJsLine[fName].has_key(str(lineIdx+1)):
					indentSize = len(jsLines[lineIdx]) -len(jsLines[lineIdx].lstrip())
					for mId in groupByJsLine[fName][str(lineIdx+1)]:
						if groupByJsLine[fName][str(lineIdx+1)][mId].has_key('m'):
							for line in groupByJsLine[fName][str(lineIdx+1)][mId]['m']:
								jsOutFP.write("%s// [MTrace] -> %s\n"%(' '*indentSize,line))




						if groupByJsLine[fName][str(lineIdx+1)][mId].has_key('u'):
							uniqueCountTable = {}
							uniqueTable = {}
							for line in groupByJsLine[fName][str(lineIdx+1)][mId]['u']:
								if uniqueCountTable.has_key("%s_%s_%s_%s_%s"%(line[0],line[2],line[3],line[7],line[8])):
									uniqueCountTable["%s_%s_%s_%s_%s"%(line[0],line[2],line[3],line[7],line[8])]+=1
									continue;
								uniqueCountTable["%s_%s_%s_%s_%s"%(line[0],line[2],line[3],line[7],line[8])]=1
								uniqueTable["%s_%s_%s_%s_%s"%(line[0],line[2],line[3],line[7],line[8])]=line
								
								# print "%s"%(line)

							for unique in uniqueTable:
								line = uniqueTable[unique]
								line[0] = "%s(%d)"%(line[0],uniqueCountTable[unique])
								# line = map(lambda x: Color('{autoyellow}%s{/autoyellow}'%(x)),line)
								# groupByJsAllocData.append([line[0],line[1],line[2],line[3],line[7],line[8]])
								# groupByJsAllocData.append(line)
								jsOutFP.write("%s// [MTrace] -> %s\n"%(' '*indentSize,line))


						if groupByJsLine[fName][str(lineIdx+1)][mId].has_key('f'):
							for line in groupByJsLine[fName][str(lineIdx+1)][mId]['f']:
								jsOutFP.write("%s// [MTrace] -> %s\n"%(' '*indentSize,line))

			jsOutFP.close()
		# print "--> ", jsLineInfos[fName][int(lineNum)],
		# codeLine = jsLineInfos[fName][int(lineNum)-1].strip("\n")
		# outFP.write("--> %s"%(codeLine))


	print "---------------------------------"
	print " group By Js Alloc"
	print "---------------------------------"

	for fName in groupByJsAlloc:
		for mId in groupByJsAlloc[fName]:
			# for aType in groupByJsAlloc[fName][mId]:
				# for line in groupByJsAlloc[fName][mId][aType]:
				# 	print "%s,%s,%s"%(line)
			groupByJsAllocData = [["Type","Address","Size","mId","stack size","stack address","mIdValue","JS Code","JS Line No"]]
			# groupByJsAllocData = [["Type","Address","Size","mId","JS Code","JS Line No"]]

			if groupByJsAlloc[fName][mId].has_key('m'):
				for line in groupByJsAlloc[fName][mId]['m']:
					line = map(lambda x: Color('{autogreen}%s{/autogreen}'%(x)),line)
					# groupByJsAllocData.append([line[0],line[1],line[2],line[3],line[7],line[8]])
					groupByJsAllocData.append(line)
					# print "%s"%(line)


			if groupByJsAlloc[fName][mId].has_key('u'):
				uniqueCountTable = {}
				uniqueTable = {}
				for line in groupByJsAlloc[fName][mId]['u']:
					if uniqueCountTable.has_key("%s_%s_%s_%s_%s"%(line[0],line[2],line[3],line[7],line[8])):
						uniqueCountTable["%s_%s_%s_%s_%s"%(line[0],line[2],line[3],line[7],line[8])]+=1
						continue;
					uniqueCountTable["%s_%s_%s_%s_%s"%(line[0],line[2],line[3],line[7],line[8])]=1
					uniqueTable["%s_%s_%s_%s_%s"%(line[0],line[2],line[3],line[7],line[8])]=line
					
					# print "%s"%(line)

				for unique in uniqueTable:
					line = uniqueTable[unique]
					line[0] = "%s(%d)"%(line[0],uniqueCountTable[unique])
					line = map(lambda x: Color('{autoyellow}%s{/autoyellow}'%(x)),line)
					# groupByJsAllocData.append([line[0],line[1],line[2],line[3],line[7],line[8]])
					groupByJsAllocData.append(line)
				

			if groupByJsAlloc[fName][mId].has_key('f'):
				for line in groupByJsAlloc[fName][mId]['f']:
					line = map(lambda x: Color('{autored}%s{/autored}'%(x)),line)
					# groupByJsAllocData.append([line[0],line[1],line[2],line[3],line[7],line[8]])
					groupByJsAllocData.append(line)
					# print "%s"%(line)


			table = SingleTable(groupByJsAllocData, "[MTrace Group By Js Allocation No. %s]"%(mId)) # ""
			table.justify_columns[2] = 'right'
			table.justify_columns[3] = 'right'
			# table.justify_columns[4] = 'right'
			# table.justify_columns[5] = 'right'
			# table.justify_columns[6] = 'right'

			if len(groupByJsAllocData) > 1:
				print table.table





	# print groupByJsAllocData


def main(argv):
	global groupByJsAlloc
	global groupByJsLine

	inFP = open(argv[0],"rb+")
	outFP = open(argv[1],"wb+")

	logLines = inFP.readlines()
	memoryTable = {}

	jsLineInfos = {}
	contextTable = {}
	contextId = 0

	groupByJsAlloc = {}
	groupByJsLine = {}


	contextTable[0] = ['unknown','?','?','?']
	contextTable[-1] = ['unknown','?','?','?']
	memoryTable['-1'] = -1
	memoryTable['0'] = 0
	for line in logLines:
		# outFP.write(line)
		line = line.strip('\r\n') 

		if line.startswith('[R') :

			fName = ""
			lineNum = 0
			colNum = 0
			codeLine = ""

			# print "Runtime Trace"
			rtInfo = line.split(":")[1]
			fName,lineNum,colNum = rtInfo.split("#")
			# print "%s,%s,%s"%(fName,lineNum,colNum)

			if jsLineInfos.has_key(fName) :
				if len(jsLineInfos[fName]) > int(lineNum)-1:
					# print "--> ", jsLineInfos[fName][int(lineNum)],
					codeLine = jsLineInfos[fName][int(lineNum)-1].strip("\n")
					# outFP.write("--> %s"%(codeLine))
			else:
				if os.path.isfile(fName):
					jsFP = open(fName,"rb+")
					jsLines = jsFP.readlines()
					jsLineInfos[fName] = jsLines
					jsFP.close()

					# print "--> ", jsLineInfos[fName][int(lineNum)],
					codeLine = jsLineInfos[fName][int(lineNum)-1].strip("\n")
					# outFP.write("--> %s"%(codeLine))
				else:
					jsLineInfos[fName] = []

			contextId += 1
			contextTable[contextId] = [fName,lineNum,colNum,codeLine]


		elif line.startswith('[m') :
			# print "malloc"
			mInfo	= line[4:].split(",")
			mId		= mInfo[2]
			memoryTable[mId] = contextId
			# memoryTable[mId] = [fName,lineNum,colNum,codeLine]

			fName,lineNum,colNum,codeLine = contextTable[contextId]
			appendLog(fName,lineNum,colNum,codeLine.strip(),mInfo,mId,'m')

		elif line.startswith('[f') :
			mInfo	= line[4:].split(",")
			mId		= mInfo[2]
			
			if contextId != memoryTable[mId]:
				fName,lineNum,colNum,codeLine = contextTable[memoryTable[mId]]
				# print "-> %s,%s,%s,%s"%(fName,lineNum,colNum,codeLine)
				# outFP.write("  -#-> %s,%s,%s,%s\n"%(fName,lineNum,colNum,codeLine))

			fName,lineNum,colNum,codeLine = contextTable[contextId]
			appendLog(fName,lineNum,colNum,codeLine.strip(),mInfo,mId,'f')
			# print "free"

		elif line.startswith('[u') :
			mInfo	= line[4:].split(",")
			mId		= mInfo[2]
			
			if contextId != memoryTable[mId]:
				fName,lineNum,colNum,codeLine = contextTable[memoryTable[mId]]
				# print "-> %s,%s,%s,%s"%(fName,lineNum,colNum,codeLine)
				# outFP.write("  -#-> %s,%s,%s,%s\n"%(fName,lineNum,colNum,codeLine))

			fName,lineNum,colNum,codeLine = contextTable[contextId]
			appendLog(fName,lineNum,colNum,codeLine.strip(),mInfo,mId,'u')

	filterLog()
	printLog()

	# outFP.close()
	inFP.close()

if __name__ == "__main__":
	if(len(sys.argv)!=3):
		print "js_symbolizer.py in.log out.log"
	
	main(sys.argv[1:])
