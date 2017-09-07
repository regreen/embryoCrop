'''
Created on Sep 5, 2017

Loads embryo images generated by CV1000 and crops/orients and saves separate embryos based on DIC (C3) central image
'''
 
date = '20140709T132509' 

loadFolder = 'Z:/'
folderIn = loadFolder + 'CV1000/' + date #Input folder
trackingFile = 'Z:/Experiment_tracking_sheets/EMBD_fileNames_Tracking_Sheet.csv'
aspectRatioFile = 'Z:/cropped/aspects.csv'
z = 18 #number of z planes
nT = 31 #number of time points
corrDrift = True
removeBG = True
attCorrect = True
apRotate = True
nWells = 14#number of wells (14)
pointVisits = 4# number of point visits (4)

import glob, csv, cv2, os, shutil
import numpy as np
from findEmbryo import showIm
from myFunc import clearFolder
from cropAPI import cropEmbs
import tkMessageBox

debug = False # use to debug the program

def getConditions(date, fileName):
    ''' loads RNAi strains for a specified date from a csv file '''
    global RNAi, strains
#     csvFile = csv.reader(open(fileName, 'rb'), delimiter=',')
    csvFile = csv.reader(open(fileName, 'rU'), delimiter=',') #universal
    fileData=[]
    for row in csvFile:
        fileData.append(row[1:-1])
    myDate = [s for s in fileData if s[0]==date]
    myDate = sorted(myDate, key=lambda well: well[2])
    RNAi = [s[3] for s in myDate]
    strains =  [s[4] for s in myDate]
    return

def loadImages(folder, well, j):
    '''
    loads images from a folder and splits them in separate point visits
    
    Parameters:
    folder : folder to read images from
    
    Return:
    allImgs: list of 4 different point visits with 3 channels in each. images are numpy arrays.
    '''
    imc1, imc2, imc3 = [], [], []
    folderNames = glob.glob(folder+'/Well{0:0>3}/*F{1:0>3}*C1.tif'.format(well,j))
    folderNames.sort()
    for fileName in folderNames:
        imc1.append(cv2.imread(fileName, -1))
        
    folderNames = glob.glob(folder+'/Well{0:0>3}/*F{1:0>3}*C2.tif'.format(well,j))
    folderNames.sort()
    for fileName in folderNames:
        imc2.append(cv2.imread(fileName, -1))
        
    folderNames = glob.glob(folder+'/Well{0:0>3}/*F{1:0>3}*C3.tif'.format(well,j))
    folderNames.sort()
    for fileName in folderNames:
        imc3.append(cv2.imread(fileName, -1))
    
    imc1 = np.reshape(imc1, (nT,z,imc1[0].shape[-2],imc1[0].shape[-1]))
    imc2 = np.reshape(imc2, (nT,z,imc2[0].shape[-2],imc2[0].shape[-1]))
    imc3 = np.reshape(imc3, (nT,z,imc3[0].shape[-2],imc3[0].shape[-1]))
    allImgs=np.stack((imc1, imc2, imc3), axis=2)
    return allImgs

def getAllEmb(folder):
    '''
    Finds and saves all embryos
    
    ParametersL
    folder: folder to load embryos
    
    Return:
    None
    '''
    global RNAi, strains
    
    print('STARTED!!!')
    getConditions(date, trackingFile)
    totalEmb = 0
    embs=[]
    
    for well in range(nWells):
        for j in range(pointVisits):
#-----------------------------------------------------------------------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------------------------------------------------------------------#
            if debug: well, j = 8, 3
            imgs = loadImages(folder, well+1, j+1)
            if imgs.size>0:
                print('loaded well {0} point {1}'.format(well+1, j+1))
                if strains[well]=='MS': featureList = [41,41,None]
                else: featureList = [201,201,None]
                es, rs = cropEmbs(imgs, 2, corrDrift, attCorrect, 0.1, removeBG, featureList, 0.315, EmbdScreen=True)
                embs.append([well, j, es, rs])
                totalEmb+=len(embs[-1])-2
            else: print('no images well {0} point {1}'.format(well+1, j+1))
            del imgs
        
    print('Done analyzing, ready to save!')
    checks = np.array([checkEmbDebris(e[2*3*z+3*z/2+2]) for well, j, es, rs in embs for e in es])
    totalEmb = checks.size
    uniqeRNAi = np.array(list(set(RNAi)))
    embN = np.ones([len(uniqeRNAi),2])
    xembN = np.ones([len(uniqeRNAi),2])
    if not debug:
        for well,j, es, rs in embs:
            if strains[well]!='MS':k=0
            else: k=1
            for l in range(len(es)):
                e=es[l]
                r=rs[l]
                print('{0} embryos left, saving...'.format(totalEmb))
                i = checks.size-totalEmb
                if checks[i]==1:
                    saveEmb(e,j,int(embN[np.where(uniqeRNAi==RNAi[well])[0],k]), well, checks[i],r)
                    embN[np.where(uniqeRNAi==RNAi[well])[0],k]+=1
                elif checks[i]==2:
                    saveEmb(e,j,int(xembN[np.where(uniqeRNAi==RNAi[well])[0],k]), well, checks[i],r)
                    xembN[np.where(uniqeRNAi==RNAi[well])[0],k]+=1
                totalEmb-=1
                

def checkEmbDebris(im):
    ''' lets user debug supplied image, and returns 1 for yes (save) and 0 for not and 2 for special case'''
    code = showIm(im)
    if code == ord('d') or code == ord('D'):
        result = tkMessageBox.askquestion("Delete", "Are You Sure?", icon='warning')
        if result == 'yes':
            return 0
        else:
            return checkEmbDebris(im)
    elif code == ord('x') or code == ord('X'): return 2
    else: return 1

def saveEmb(imgs, point, i, well, check, r):
    '''
    Saves embryo images according to a certain pattern
    
    Parameters:
    imgs: numpy array with images in czt order
    f: point visit number
    i: embryo number
    r: aspect ratio
    '''
    
    imgs = np.reshape(imgs,(nT, z, 3, imgs.shape[-2], imgs.shape[-1]))
    im1 = imgs[:,:,0]
    im2 = imgs[:,:,1]
    im3 = imgs[:,:,2]
    strain = strains[well]
    ri = RNAi[well]
    if ri!='EMBD0000': folderOut = loadFolder + 'cropped/{0}/{1}/'.format(ri,strain) #outputFolder
    else: folderOut = loadFolder + 'cropped/EMBD0000/{0}/{1}/'.format(strain,date) #outputFolder
    if check == 2 :folderOut = folderOut+'x'
    else: folderOut = folderOut
    j = 1
    folder = folderOut+ 'Emb{0}/'.format(j)
    while os.path.exists(folder):
        fileName = glob.glob(folder+'*_T01_Z01_C1.tif')
        if len(fileName)>0:
            fileName = fileName[0].split('/')[-1]
            if fileName.split('_')[2]==date:
                if i==1: break
                else: i -= 1
            j += 1
            folder = folderOut+ 'Emb{0}/'.format(j)
        else:
            j += 1
            folder = folderOut+ 'Emb{0}/'.format(j)
    fileName = '{0}_Emb{1}_{2}_W{3:0>2}F{4}_'.format(ri,j,date,well+1,point+1)
    
    ''' correct attenuation and save local '''
    if not os.path.exists(folder): os.makedirs(folder)
    else:
        print('file exist, clearing folder', folder)
        clearFolder(folder)
        if os.path.exists(folder+'batch-output'):
            shutil.rmtree(folder+'batch-output')
    saveImgs(im1, folder, fileName,1)
    saveImgs(im2, folder, fileName,2)
    saveImgs(im3, folder, fileName,3)
        
    ''' populate aspect ratio file '''
    print('saveEmb aspect j=',j)
    addAspect(r,date, ri, j)
 
def saveImgs(imgs,folder, fileName, c):
    for i in range(len(imgs)):
        cv2.imwrite(folder+fileName+'T{0:0>2}_Z{1:0>2}_C{2}.tif'.format( i/z+1, i%z+1, c), imgs[i])

def addAspect(r, date, ri, j):
    '''
    Adds aspect ratio of an embryo into the csv file
    
    Parameters:
    r: aspect ratio
    date: date
    ri: RNAi conditions
    j: embryo number
    '''
    
    import operator
    newData = []
    oldData = loadAspects(aspectRatioFile)
    i=0
    while i<len(oldData):
        if oldData[i][0]!=ri: newData.append(oldData[i])
        elif oldData[i][1]!=date: newData.append(oldData[i])
        elif int(oldData[i][2])<j: newData.append(oldData[i])
        i+=1
    newData.append([ri, date, '{0:0>3}'.format(j), str(r)])
    newData = sorted(newData, key=operator.itemgetter(1, 2, 3))
    saveAspects(aspectRatioFile, newData)

def loadAspects(fileName):
    '''
    reads aspect ratios from file. The aspect ratios are sorted by rnai condition, date, embryo number.
    fileName: name of the file to read from
    '''
    fileData = []
    try:
        csvFile = csv.reader(open(fileName, 'rU'), delimiter=',') #universal
        for row in csvFile:
            fileData.append(row)
    except: pass
    return fileData

def saveAspects(fileName, data):
    with open(fileName, 'wb') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerows(data)

if __name__ == '__main__':
    getAllEmb(folderIn)
    print('ALL DONE!!!!! :)')