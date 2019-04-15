# -*- coding: utf-8 -*-
"""
Created on Sun Jul 22 14:32:58 2018

@author: Patrik
"""

import math
from numpy.linalg import norm
import numpy as np
import os
from pyexcel_ods import get_data



def cubitalindex(p4, p5, p6):
    # Calculate the factor of the euclidean p4-p5 and p5-p6
    return np.around(norm(p4-p5)/norm(p5-p6), decimals=3)

def closestPointOnLine(a, b, p):
    ap = p-a
    ab = b-a
    result = a + np.dot(ap,ab)/np.dot(ab,ab) * ab
    return result

def discoidalvinkel(p1, p2, p3, p7):
    # Calculate p3 projection on p1-p2 as p3_proj
    p3_proj = closestPointOnLine(p1, p2, p3)
    ab = p3_proj - p3
    ap = p3_proj - p7

    ##print(p3_proj)
    # Caclulate angle between the two vectors ab and ap by using the corss product
    # Cross product are definded as cross(a,b) = abs(a)*abs(b)*sin(angle)
    # Hence we have angle = arcsin(cross(a,b) / (abs(a)*abs(b)))
    angle = math.asin(np.cross(ab,ap)/(norm(ap)*norm(ab)))
    #print(angle)
    #print(180/math.pi)
    #print(angle*180/math.pi)
    angle = angle*180/math.pi
    angle = np.around(angle, decimals=3)
    return angle*-1


# finds files with certain extension
# works only with one 'dot' in file name    
def findFilesExt(ext):
    fileNames = np.array([], dtype=str)
    for f in os.listdir():
        #print(f)
        f_name, f_ext = os.path.splitext(f)
        #print(f_name, f_ext)
        if f_ext==ext:
            #print(f)
            fileNames = np.append(fileNames, f)
    return fileNames

#reads Mellving files (.ving) and parse data
def readMellwingFile(lines):
    i = 0
    foundWing = False
    countWings = 0
    wingDataIn = np.array([],dtype=int)    
    for line in lines:
        line = line.strip()
        if line.find("Vinge") ==-1 and foundWing == True:
            #wingDataIn = np.append(wingDataIn, int(line))
            wingDataIn = np.append(wingDataIn, float(line))
        if line.find("Vinge") != -1 :
            foundWing = True
            countWings = countWings + 1
        i = i+1
    wingDataIn = np.resize(wingDataIn,[countWings,14])
    return wingDataIn

#reads CBeewing files (.pos) and parse data
def readCBeeWingFile(lines):
    countWings=0
    wingDataIn = np.array([])
    for line in lines:
        line = line.strip()
        #print(line)
        lineFloat = np.array([])    
        if line.find('#') ==-1:
            #print(line)
            countWings = countWings+1
            line = line.replace(",", ".")
            line = line.replace("  ", " ")
            line = line.split(' ')
        
            #convert string to float
            for i in range(0,len(line)):
                lineFloat = np.append(lineFloat, float(line[i]))
            #.pos file consist of 8 points (x,y) point 4 is for Hantel measurement    
            lineFloat = np.delete(lineFloat, [6,7])
            wingDataIn = np.append(wingDataIn, lineFloat)
        wingDataIn = np.resize(wingDataIn,[countWings,14])    
    return wingDataIn

def writeCsv(f_outDir, f_name, wingData):   
    import csv
    rows, cols = wingData.shape
    fnameW = "bee-wing-" + f_name
    fnameCsv = f_outDir + "bee-wing-" + f_name + '-x.csv'

    with open(fnameCsv, 'w', newline='') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',')
        filewriter.writerow(['Image', 'x1', 'y1', 'x2', 'y2', 'x3', 'y3', 'x4', 'y4', 'x5', 'y5', 'x6', 'y6', 'x7', 'y7', 'Ci', 'Dv'])
        for x in range(0,rows):
              #print("row ", x)
              dataToWrite = np.array([])
              imageName = fnameW + "-" + str(x+1) + ".jpg"
              dataToWrite = np.append(dataToWrite, imageName)
              dataToWrite = np.append(dataToWrite, wingData[x])
              Ci = cubitalindex(wingData[x,[6,7]],wingData[x,[8,9]],wingData[x,[10,11]]) #(p4, p5, p6)
              dataToWrite = np.append(dataToWrite, Ci)
              Dv = discoidalvinkel(wingData[x,[0,1]],wingData[x,[2,3]],wingData[x,[4,5]], wingData[x,[12,13]]) #(p1, p2, p3, p7)
              dataToWrite = np.append(dataToWrite, Dv)
              #print(imageName)
              #print(wingData[x])
              #print(Ci, Dv)
              #print(dataToWrite)                         
              filewriter.writerow(dataToWrite)
              
def writeJson(f_outDir, file, wingData):
    import json
    import datetime
    rows, cols = wingData.shape
    f_name, f_ext= file.split('.')
    
    now = datetime.datetime.now()
    fnameW = "bee-wing-" + f_name
    fnameJson = f_outDir + "bee-wing-" + f_name + '-x.json'

    data = {}
    data['meta'] = {}
    data['meta'] = {'parsed file': file ,'date parsed': now.strftime("%Y-%m-%d")}
    data['wings']=[]
    for x in range(0,rows):
        imageName = fnameW + "-" + str(x+1) + ".jpg"
        data['wings'].append({'image': imageName, 
               'x1': wingData[x,0],
               'y1': wingData[x,1],
               'x2': wingData[x,2],
               'y2': wingData[x,3],
               'x3': wingData[x,4],
               'y3': wingData[x,5],
               'x4': wingData[x,6],
               'y4': wingData[x,7],
               'x5': wingData[x,8],
               'y5': wingData[x,9],
               'x6': wingData[x,10],
               'y6': wingData[x,11],
               'x7': wingData[x,12],
               'y7': wingData[x,13],
               'Ci': cubitalindex(wingData[x,[6,7]],wingData[x,[8,9]],wingData[x,[10,11]]), #(p4, p5, p6)}
               'Dv': discoidalvinkel(wingData[x,[0,1]],wingData[x,[2,3]],wingData[x,[4,5]], wingData[x,[12,13]]) #(p1, p2, p3, p7)
               })
        #print(data)
        with open(fnameJson, 'w') as jsonfile:
            json.dump(data, jsonfile, indent=2)
            
              

#inDir mandatory
#outDir set directory or pass '' for same as input directory
def parseMellwingFiles(inDir, outDir):
    print("Converting Mellwing files")
    os.chdir(inDir)
    files = findFilesExt('.ving')
    if len(files) == 0:
        print("No Mellwing (.ving) files found")
    #print(files)
    wingData = np.array([],dtype=int)

    for ff in files:
        file = ff
        print("Conv:", file, "\tfrom:\t", inDir)
        #print(file)
        #file = "Stavershult-acb-1704.ving"
        #file = f__path + f__name1
        f_name, f_ext= file.split('.')

        f = open(file, "r")
        lines = f.readlines()
        f.close

        wingData = readMellwingFile(lines)
        #writeCsv(outDir, f_name, wingData)
        writeJson(outDir, file, wingData)
        print("Done:", file, "\tto:\t", outDir)

#inDir mandatory
#outDir set directory or pass '' for same as input directory
def parseCBeeWingFiles(inDir, outDir):
    print("Converting CBeeWing files")
    os.chdir(inDir)
    files = findFilesExt('.pos')
    if len(files) == 0:
        print("No CBeeWing (.pos) files found")
    #print(files)
    wingData = np.array([],dtype=int)
    
    for ff in files:
        file = ff
        print("Conv:", file, "\tfrom:\t", inDir)
        f_name, f_ext= file.split('.')

        f = open(file, "r")
        lines = f.readlines()
        f.close

        wingData = readCBeeWingFile(lines)
        #writeCsv(outDir, f_name, wingData)
        writeJson(outDir, file, wingData)
        print("Done:", file, "\tto:\t", outDir)
        
        
        
def parseOdsWingFiles(inDir, outDir):
    print("Converting .ods wing files")
    os.chdir(inDir)
    files = findFilesExt('.ods')
    if len(files) == 0:
        print("No wingindex (.ods) files found")
    #print(files)
    ##wingData = np.array([],dtype=int)
    
    for ff in files:
        file = ff
        print("Conv:", file, "\tfrom:\t", inDir)
        #file = "lillangen-pt-svarm.pos"
        #file = f__path + f__name1
        f_name, f_ext= file.split('.')

        #data = get_data("C:\\Homeroot\\00Biodling\\bee\\WingDataFiles\\bee\\wings\\WingIndexFiles\\Unformated\\Boris 3.ods")
        data = get_data(file)

        ##wingData = readCBeeWingFile(lines)
        #writeCsv(outDir, f_name, wingData)
        ##writeJson(outDir, file, wingData)
        print("Done:", file, "\tto:\t", outDir)

        now = datetime.datetime.now()

        wings = []
        startRow = 3
        for row in data["Data"][startRow:]:
            if row[0] =='' :
                break
            wing = {}
            wing["image"] = f_name + "-" + str(startRow-2) + ".jpg"
            wing["x1"] = row[0]
            wing["y1"] = row[1]
            wing["x2"] = row[2]
            wing["y2"] = row[3]
            wing["x3"] = row[4]
            wing["y3"] = row[5]
            wing["x4"] = row[6]
            wing["y4"] = row[7]
            wing["x5"] = row[8]
            wing["y5"] = row[9]
            wing["x6"] = row[10]
            wing["y6"] = row[11]
            wing["x7"] = row[12]
            wing["y7"] = row[13]
            wing["Ci"] = vingindex1.cubitalindex(np.array([row[6], row[7]]), np.array([row[8], row[9]]), np.array([row[10], row[11]]))
            wing["Dv"] = vingindex1.discoidalvinkel(np.array([row[0], row[1]]), np.array([row[2], row[3]]), np.array([row[4], row[5]]), np.array([row[12], row[13]]))
            wings.append(wing)
            #print(wing)
            startRow = startRow + 1

            
            data = {}
            data["meta"] = {}
            data["meta"]["parsed file"] = file
            data["meta"]["date parsed"] = now.strftime("%Y-%m-%d")
            data["wings"] = wings
            #print(wings)
            with open(outDir + f_name + '.json', 'w') as outfile:  
                json.dump(data, outfile)

#Run through all mellwing files (.ving) and format them and save them to .csv
#Run through all CBeeWing files (.pos) and format them and save them to .csv

#os.chdir('/Homeroot/00Biodling/Datafiler/AnnCharlotte/Datafiler/')

storeDir = 'C:\\Homeroot\\00Biodling\\Datafiler\\ConvertedWingIndexFiles\\'
#storeDir = ''

#Run Ann Charlottes files
inputDir = 'C:\\Homeroot\\00Biodling\\Datafiler\\ACB-AnnCharlotte\\Datafiler\\'

parseMellwingFiles(inputDir, storeDir)
parseCBeeWingFiles(inputDir, storeDir)

#Run Per Thunmans files
inputDir =  'C:\\Homeroot\\00Biodling\\Datafiler\\PT-PerThunman\\'

parseMellwingFiles(inputDir, storeDir)
parseCBeeWingFiles(inputDir, storeDir) 

#Run Ingvar Pettersson files




#Run Per Thunmans files
inputDir = 'C:\\Homeroot\\00Biodling\\bee\\WingDataFiles\\bee\\wings\\WingIndexFiles\\Unformated\\'
parseOdsWingFiles(inputDir, storeDir)


"""
inputDir =  'C:/Homeroot/00Biodling/Datafiler/PerThunman/'            
outDir = '/Homeroot/00Biodling/Datafiler/csvConvertedFiles/'
outDir = '/Homeroot/00Biodling/Datafiler/PerThunman/'
file = 'GF.pos'
file = 'PT-09002.pos'
file = 'lillangen-pt-svarm.pos'
#f_name= 'testingJson.json'

f_name, f_ext= file.split('.')
            
f = open(file, "r")
lines = f.readlines()
f.close

wingData = readCBeeWingFile(lines)
            

writeJson(outDir, file, wingData)
"""







