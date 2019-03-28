import argparse
import cv2
import numpy as np
import pprint
import time
import sys
import keyboard
import os
from matplotlib import pyplot as plt

def getAABBfromContour(contour):
    min_x = contour[0][0][0]
    max_x = contour[0][0][0]
    min_y = contour[0][0][1]
    max_y = contour[0][0][1]
    for j in range(0,len(contour)):
        if contour[j][0][0] < min_x:
            min_x = contour[j][0][0]
        if contour[j][0][0] > max_x:
            max_x = contour[j][0][0]
        if contour[j][0][1] < min_y:
            min_y = contour[j][0][1]
        if contour[j][0][1] > max_y:
            max_y = contour[j][0][1]
    return (min_x, min_y, max_x, max_y)


def getThresholdMask(image):
    imgray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Blur to get rid of noice
    imblur = imgray
    for i in range(0, 10):
        imblur = cv2.GaussianBlur(imblur,(17,17),0)
    ret, mask = cv2.threshold(imblur, 127, 255, 0)
#    cv2.imshow('Gray',imgray)
#    cv2.imshow('Blur',imblur)
    height, width = mask.shape
    mask = cv2.rectangle(mask,(0,0),(width-1,height-1),(255,255,255),2)
#    cv2.imshow('Threshold',mask)
    return mask

def getWingContours(mask, image):
    filtered_contours = []
    im_cont, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    print(len(contours))
    for i in range(0, len(contours)):
#        image2 = cv2.drawContours(image, [contours[i]], 0, (0,255,0), 5)
#        cv2.imshow('Contours' + str(i), image2)
        if len(contours[i]) < 300:
            print("Too few points " + str(len(contours[i])))
            continue
        (x1 , y1, x2, y2) = getAABBfromContour(contours[i])
        if x2-x1 < 300 or x2-x1 > 600:
            print("Not correct width " + str(x2-x1))
            continue
        filtered_contours.append(contours[i])

    return filtered_contours

def getImageFromStr(image_str):
    nparr = np.fromstring(image_str, np.uint8)
    img = cv2.imdecode(nparr,cv2.IMREAD_COLOR)
    return img

def storeWings(db, acb, image, wing_contours):
    margin = 10
    print("Store " + str(len(wing_contours)) + " images")
    for i in range(0, len(wing_contours)):
        (x1 , y1, x2, y2) = getAABBfromContour(wing_contours[i])
        h,w,c = image.shape
        x1 -= margin
        y1 -= margin
        x2 += margin
        y2 += margin
        if (x1 < 0):
            x1 = 0
        if (y1 < 0):
            y1 = 0
        if (x2 > w):
            x2 = w
        if (y2 > h):
            y2 = h

        src_region = image[y1:y2, x1:x2]
        cv2.imwrite('wings/wing' + str(i+1)+'.jpg', src_region)
#        db.storeWing({
#            "acb" : acb,
#            "index" : i+1,
#            "image" : cv2.imencode('.jpg', src_region)[1].tostring()
#        })
#    db.updateNrOfWings({
#        "acb" : acb,
#        "nr_of_wings": len(wing_contours)
#    })

def createWings(acb):
    hivedb = HiveDB()
    result = hivedb.loadHive(acb)
    if (result):
        hivedb.removeWings(acb)
        image = getImageFromStr(result["wings"])
        mask = getThresholdMask(image)
        wing_contours = getWingContours(mask, image)
        storeWings(hivedb, acb, image, wing_contours)
        cv2.imshow('Original',image)


def main(filename, drawGraphs):
    print("Hej parsing ["+filename+"]")
    image =  cv2.imread(filename)
    hist = cv2.calcHist([image],[0],None,[256],[0,256])
    if (drawGraphs):
        print("Kill histogram to continue")
        cv2.imshow('Original',image)
        plt.plot(hist)
        plt.xlim([0,256])
        plt.show()

    mask = getThresholdMask(image)
    if (drawGraphs):
        cv2.imshow('Mask',mask)
    wing_contours = getWingContours(mask, image)
    #cv2.imshow('contours',wing_contours)
    print ("Found " + str(len(wing_contours)) + " possible wings")
    for contours in wing_contours:
        (x1 , y1, x2, y2) = getAABBfromContour(contours)
        print(str(x1) + ", " + str(y1) + ", " + str(x2) + ", " + str(y2))
        image = cv2.rectangle(image,(x1,y1),(x2,y2),(255,0,0),5)
    if (drawGraphs):
        cv2.imshow('KKK',image)
    print(os.path.basename(filename))
    cv2.imwrite('contours/' + os.path.basename(filename), image)
    #while True:
    #    try:
    #        if keyboard.is_pressed('q'):
    #            print('You Pressed q Key!')
    #            break
    #        else:
    #            time.sleep(1)
    #            pass
    #    except:
    #        print('You Pressed A Key!')
    #        break

    if (drawGraphs):
        print("Press q in one of the graphs to exit" )
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def usage():
    print("Usage:")
    print("  " + sys.argv[0] + " <Strip file>")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Find wings in a wing strip image file')
    parser.add_argument('StripImageFile', action="store",
                   help='the strip image to parse')

    parser.add_argument('--show', action='store_true',
                   help='Draw graphs along the way')
    
    parser.add_argument('-s', '--silent', action='store_true',
                   help='Do not print any information')
    
    args = parser.parse_args(sys.argv[1:])
    print(str(args))
    main(args.StripImageFile, args.show)


