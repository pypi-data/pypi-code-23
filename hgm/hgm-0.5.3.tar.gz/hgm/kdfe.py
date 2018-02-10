# 

# Author: Bing SHI
# Institution: City University of Hong Kong
# Date: 2017.7~2017.12
# Function： KeyPoint detection and features extraction for graph matching.
# Using: python kdfe.py fm1 fm2    
# fm1, fm2 are respectively main name of two image files.

import os
import sys
import numpy as np
import cv2
from matplotlib import pyplot as plt
from copy import deepcopy

# parameters setting
RATIO = 0.80        # According to the need to change.

def siftdetext(f1, f2):
    '''
    Function： KeyPoint detection and features extraction for graph matching.
    Using: python kdfe.py fm1 fm2    
    here, fm1, fm2 are respectively main name of two image files.
    '''
    MIN_MATCH_COUNT = 10  
    fn1, ext = os.path.splitext(f1)
    fn2, ext = os.path.splitext(f2)
    #--1-- read images
    img1 = cv2.imread(f1,0)          # queryImage
    img2 = cv2.imread(f2,0)          # trainImage   
    #--2-- detecte keypoints and extract SIFT features    
    sift = cv2.xfeatures2d.SIFT_create()          
    # find the keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(img1,None)  
    kp2, des2 = sift.detectAndCompute(img2,None)
    #--3-- matching
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks = 50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1,des2,k=2)
    #--4-- ratio test.   
    good = []
    for m,n in matches:
        if m.distance < RATIO * n.distance:
            good.append(m) 
    print('good matching: %d'%len(good))    
    # Homography   
    if len(good) > MIN_MATCH_COUNT:
        src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
        dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
        matchesMask = mask.ravel().tolist()                # corresponding to good
        h,w = img1.shape                                   # h,w,d = img1.shape for color image
        pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
        dst = cv2.perspectiveTransform(pts,M)
        #img2 = cv2.polylines(img2,[np.int32(dst)],True,255,3, cv2.LINE_AA)
    else:
        print("Not enough matches are found - %d/%d" % (len(good),MIN_MATCH_COUNT))
        matchesMask = None       
    #--5-- draw matches
    draw_params = dict(matchColor = (0,255,0),     # draw matches in green color  
                       singlePointColor = None,
                       matchesMask = matchesMask,  # draw only inliers
                       flags = 2)
    img3 = cv2.drawMatches(img1,kp1,img2,kp2,good,None,**draw_params)
    plt.imshow(img3, 'gray');     plt.show()
    #--6-- save results--
    mm=np.asarray(matchesMask)
    src = [[kp1[m.queryIdx].pt[0],kp1[m.queryIdx].pt[1]] for m in good ] 
    srcarr = np.asarray(src)
    srcarr1 = srcarr[mm==1]
    np.savetxt(fn1+'.kps.txt',srcarr1,fmt='%f %f',newline='\r\n')
    desind1 = [m.queryIdx for m in good ]
    des12 = des1[desind1]
    desi1 = des12.astype(int)
    desi3 = desi1[mm==1]
    np.savetxt(fn1+'.des.txt',desi3,fmt='%d '*128,newline='\r\n') 
    
    dst = [[kp2[m.trainIdx].pt[0],kp2[m.trainIdx].pt[1]] for m in good ]
    dstarr= np.asarray(dst)
    dstarr1 = dstarr[mm==1]
    np.savetxt(fn2+'.kps.txt',dstarr1,fmt='%f %f',newline='\r\n')    
    desind2 = [m.trainIdx for m in good ]
    des22 = des2[desind2]    
    desi2=des22.astype(int)   
    desi4 = desi2[mm==1]
    np.savetxt(fn2+'.des.txt',desi4,fmt='%d '*128,newline='\r\n') 
# End

if __name__ == "__main__":
    siftdetext(sys.argv[1], sys.argv[2])
