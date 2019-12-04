#!/bin/python3
from clean import csvwParser as parser
import json
import os
import sys

#Function to remove not required CSVs
def selectionFormatter(selection):
    result = {}
    for tm in selection:
        result[selection[tm]['source']] = selection[tm]['columns']
    return result
def csvwFilter(csvw, selection):
    selection = selectionFormatter(selection)
    result = {'@context':csvw['@context'], 'tables':[]}
    for table in csvw['tables']:
        title = parser.getTableTitle(table)
        if(title in selection.keys()):
            table['filteredRowTitles'] = selection[title]
            result['tables'].append(table)
    return result
#Function to call the bash Scripts files and send the scvw data.
def scriptCaller(data):
    #TODO BUSCAR LA FORMA DE MANEJAR LOS NOMBRE DE LOS CSVs 
    url = parser.getUrl(data).split("/")[-1:][0]
    #url = url.split('.')[0]
    #print("********************" + url + "***************************")
    data = parser.filterCols(data)
    #print(str(data).replace('\'', '"'))
    titles = parser.getTitles(data)
    insertTitles(titles, url)
    #print("InsertTitles Done")
    replaceCsvFormat(parser.getGsubPatterns(data), url)
    titles['header'] = False
    insertTitles(titles, url)
    
    '''
    #rowSkipper(parser.getSkipRows(data), url)
    print("Skip Rows Done")
    replaceDelimiter(parser.getDelimiter(data), url)
    print("Replace Delimiter Done")
    dateFormatReplacer(parser.getDateFormat(data), url)
    print("DateFormat Changer Done")
    #booleanFormatReplacer(parser.getBooleanFormat(data), url)
    print("BooleanFormat Changer Done")
    nullFormatChanger(parser.getNullValues(data), url)
    print("NullFormat Changer Done")
    defaultEmptyStringFormatChanger(parser.getDefaultEmptyStringValue(data), url)
    '''
'''
Insert row titles (from csvw:rowTitles)
'''
def insertTitles(data, path):
    print("**********TEST***************")
    print("Titles: " + str(data['result']))
    print("Header: " + str(data['header']))
    if not data['header']:
        os.system('bash ./bash/insertTitles.sh \'%s\' %s'%(data['result'], path))


'''
#Skip rows (csvw:skipRows -> remove the first n rows)
'''
#If the skipRow is bigger than 0 the function execute the BashScritp
def rowSkipper(data, path):
    if(int(data)> 0):
        os.system('bash ./bash/skipRows.sh %s %s'%(data, path))

'''
#Delimiter (csvw:delimiter -> change to comma)
'''
def replaceDelimiter(data, path):
    delimiter = data['delimiter'].encode('unicode-escape').decode('ascii')
    arg = str(data['arg'])
#    print("Delimiter: " + delimiter.encode('unicode-escape') + " File: " + path)
    if(delimiter != ','):
        os.system('bash ./bash/delimiterReplacer.sh \'%s\' \'%s\' %s'%(delimiter,arg,path))

'''
Dates and booleans format (csvw:format -> sql formats)
'''
def dateFormatReplacer(data, path):
    try:
        if(len(data) > 0):
            for date in data:
                if(not date['correct']):
#                print("%s %s %s %s"%(date['args'],date['col'],date['delimiter'], path))
                    os.system('bash ./bash/optimized/allInOneFile \'%s\' \'%s\' \'%s\' \'%s\' \'%s\''%(date['args'],date['col'],date['delimiter'], date['arg2'], path))
    except:
        sys.exit()
def booleanFormatReplacer(data, path):
    print(data)
    
    for col in data:
        os.system('bash ./bash/booleanFormatChanger.sh %s %s %s %s'%(col['true'], col['false'], col['col'], path))

def nullFormatChanger(data, path):
    #METER PATTERN GSUB DESDE ARG1
    '''
    for col in data:
        print("Col:%s Null:%s"%(col['col'], col['null']))
    '''
    os.system('bash ./bash/nullFormatChanger.sh \'%s\' %s'%(data, path))
def defaultEmptyStringFormatChanger(data, path):
    for col in data:
        os.system('bash ./bash/defaultEmptyStringReplacer.sh \'%s\' %s %s'%(col['default'], col['col'], path))

def replaceCsvFormat(data, path):
    os.system('bash bash/csvFormatter \'%s\' \'%s\' \'%s\' \'%s\' \'%s\''%(str(data['delimiter']), str(data['gsub']),str(data['print']),str(data['split']),str(path)))

def csvFormatter(csvSelection):
    csvw = parser.jsonLoader('./tmp/annotations/annotations.json')
    csvw = csvwFilter(csvw, csvSelection)
    #print("Here" +str(csvw).replace('\'', '"'))
    for table in csvw['tables']:
        scriptCaller(table)