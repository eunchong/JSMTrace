#!/usr/bin/python
#-*- coding: utf-8 -*-

import sys
import os
from terminaltables import AsciiTable,SingleTable
from colorclass import Color, Windows
from JSMTrace.database import JSMT_DB
from collections import defaultdict

def main(argv):
	db = JSMT_DB()
	result = db.get_group_by_mid(argv[0])

	res = defaultdict(list)
	tableTitle = [["Type","Address","Size","mId","stack size","stack address","JS Code","JS Line No"]]

	for rType, rAddress,rSize,rMid,rStackSize,rStackAddress,rJSCode,rJSLineNo in result: res[rMid].append([rType, rAddress,rSize,rMid,rStackSize,rStackAddress,rJSCode,rJSLineNo])
	formated_results = [x for x in res.items()]
	for result_by_mid in formated_results:
		mId = result_by_mid[0]
		mRows = result_by_mid[1]

		groupByJsAllocData = tableTitle
		for line in mRows:
			if line[0] == "alloc":
				line = map(lambda x: Color('{autogreen}%s{/autogreen}'%(x)),line)		
			if line[0] == "load":
				line = map(lambda x: Color('{autoyellow}%s{/autoyellow}'%(x)),line)		
			if line[0] == "store":
				line = map(lambda x: Color('{autoyellow}%s{/autoyellow}'%(x)),line)		
			if line[0] == "free":
				line = map(lambda x: Color('{autored}%s{/autored}'%(x)),line)		
			groupByJsAllocData.append(line)

		table = SingleTable(groupByJsAllocData, "[MTrace Group By Js Allocation No. %s]"%(result_by_mid[0])) # ""
		table.justify_columns[2] = 'right'
		table.justify_columns[3] = 'right'

		if len(groupByJsAllocData) > 1:
			print table.table


if __name__ == "__main__":
	if(len(sys.argv)!=2):
		print "jsmt_table_viewer.py taskId"
	
	main(sys.argv[1:])

