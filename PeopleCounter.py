import numpy as np
import cv2 as cv
import Person
import time


try:
    log = open('log.txt',"w")
except:
    print( "Can't open log file")


#Entry and exit counters
cnt_up   = 0
cnt_down = 0


cap = cv.VideoCapture(r'C:\Users\shrut\OneDrive\Desktop\CrowdSense\CrowdSense\Test Files\TestVideo\TestVideo.avi')


h = 520
w = 640
frameArea = h*w
areaTH = frameArea/250
print( 'Area Threshold', areaTH)

#Entry/exit lines
line_up = int(2*(h/5))
line_down   = int(3*(h/5))

up_limit =   int(1*(h/5))
down_limit = int(4*(h/5))

print( "Red line y:",str(line_up))
print( "Blue line y:", str(line_down))
line_down_color = (255,0,0)
line_up_color = (0,0,255)
pt1 =  [0, line_down];
pt2 =  [w, line_down];
pts_L1 = np.array([pt1,pt2], np.int32)
pts_L1 = pts_L1.reshape((-1,1,2))
pt3 =  [0, line_up];
pt4 =  [w, line_up];
pts_L2 = np.array([pt3,pt4], np.int32)
pts_L2 = pts_L2.reshape((-1,1,2))

pt5 =  [0, up_limit];
pt6 =  [w, up_limit];
pts_L3 = np.array([pt5,pt6], np.int32)
pts_L3 = pts_L3.reshape((-1,1,2))
pt7 =  [0, down_limit];
pt8 =  [w, down_limit];
pts_L4 = np.array([pt7,pt8], np.int32)
pts_L4 = pts_L4.reshape((-1,1,2))

#Background subtractor
fgbg = cv.createBackgroundSubtractorMOG2(detectShadows = True)

#Structuring elements for morphological filters for removing the noise
kernelOp = np.ones((3,3),np.uint8)
kernelOp2 = np.ones((5,5),np.uint8)
kernelCl = np.ones((11,11),np.uint8)

#Variables
font = cv.FONT_HERSHEY_SIMPLEX
persons = []
max_p_age = 5
pid = 1

width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))


fourcc = cv.VideoWriter_fourcc(*'h264')  # Specify the codec
out = cv.VideoWriter('output_frame.mp4', fourcc, 20.0, (width,height))  # Adjust the parameters as needed
out2 = cv.VideoWriter("output_mask.mp4", fourcc, 20.0, (width,height), isColor=False)



while(cap.isOpened()):

   #Read an image from the video source
    ret, frame = cap.read()


    for i in persons:
        i.age_one() #age every person one frame
    #########################
    #  PRE-PROCESSING  #
    #########################
    
   #Apply background subtraction
    fgmask = fgbg.apply(frame)
    fgmask2 = fgbg.apply(frame)

   #Binariazcion to eliminate shadows (gray color)
    try:
        ret,imBin= cv.threshold(fgmask,200,255,cv.THRESH_BINARY)
        ret,imBin2 = cv.threshold(fgmask2,200,255,cv.THRESH_BINARY)
       #Opening (erode->dilate) to remove noise.((shrinking)
        mask = cv.morphologyEx(imBin, cv.MORPH_OPEN, kernelOp)
        mask2 = cv.morphologyEx(imBin2, cv.MORPH_OPEN, kernelOp)
        #Closing (dilate -> erode) to close white regions.(expanding)
        mask =  cv.morphologyEx(mask , cv.MORPH_CLOSE, kernelCl)
        mask2 = cv.morphologyEx(mask2, cv.MORPH_CLOSE, kernelCl)
    except:
        print('EOF')
        print( 'UP:',cnt_up)
        print ('DOWN:',cnt_down)
        break
    #################
    #   CONTOURS(boundaries)   #
    #################
    
    # RETR_EXTERNAL returns only extreme outer flags(Contours). All child contours are left behind.
    # CHAIN_APPROX_SIMPLE compresses horizontal,vertical and diagonal segments along the contours and leave only their end points
    contours0, hierarchy = cv.findContours(mask2,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)
    for cnt in contours0:
        area = cv.contourArea(cnt)
        if area > areaTH:
            #################
            #   TRACKING    #
            #################
            
            #Need to add conditions for multi-person, screen exits and entrances.     
            M = cv.moments(cnt)     # M object creates a dictionary of points of boundary of people detected
            
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            x,y,w,h = cv.boundingRect(cnt)

            new = True
            if cy in range(up_limit,down_limit):
                for i in persons:
                    if abs(x-i.getX()) <= w and abs(y-i.getY()) <= h:
                        # the object is close to one that was detected before
                        new = False
                        i.updateCoords(cx,cy)   #updates coordinates in the object and resets age
                        if i.going_UP(line_down,line_up) == True:
                            cnt_up += 1;
                            print( "ID:",i.getId(),'crossed going up at',time.strftime("%c"))
                            log.write("ID: "+str(i.getId())+' crossed going up at ' + time.strftime("%c") + '\n')
                        elif i.going_DOWN(line_down,line_up) == True:
                            cnt_down += 1;
                            print( "ID:",i.getId(),'crossed going down at',time.strftime("%c"))
                            log.write("ID: " + str(i.getId()) + ' crossed going down at ' + time.strftime("%c") + '\n')
                        break
                    if i.getState() == '1':
                        if i.getDir() == 'down' and i.getY() > down_limit:
                            i.setDone()
                        elif i.getDir() == 'up' and i.getY() < up_limit:
                            i.setDone()
                    if i.timedOut():
                        #remove i from the persons list
                        index = persons.index(i)
                        persons.pop(index)
                        del i     #free i memory
                if new == True:
                    p = Person.MyPerson(pid,cx,cy, max_p_age)
                    persons.append(p)
                    pid += 1     
            #################
            #   DRAWINGS    #
            #################
            cv.circle(frame,(cx,cy), 5, (0,0,255), -1)
            img = cv.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)            
            
            
   #END for cnt in contours0
            
    
        
    #################
    #   imagination    #
    #################
    str_up = 'UP: '+ str(cnt_up)
    str_down = 'DOWN: '+ str(cnt_down)
    frame = cv.polylines(frame,[pts_L1],False,line_down_color,thickness=2)
    frame = cv.polylines(frame,[pts_L2],False,line_up_color,thickness=2)
    frame = cv.polylines(frame,[pts_L3],False,(255,255,255),thickness=1)
    frame = cv.polylines(frame,[pts_L4],False,(255,255,255),thickness=1)
    cv.putText(frame, str_up ,(10,40),font,0.5,(255,255,255),2,cv.LINE_AA)
    cv.putText(frame, str_up ,(10,40),font,0.5,(0,0,255),1,cv.LINE_AA)
    cv.putText(frame, str_down ,(10,90),font,0.5,(255,255,255),2,cv.LINE_AA)
    cv.putText(frame, str_down ,(10,90),font,0.5,(255,0,0),1,cv.LINE_AA)



    out.write(frame)
    out2.write(mask)
    
    cv.imshow('Frame',frame)
    cv.imshow('Mask',mask)    
    
    
    #press Q to exit
    k = cv.waitKey(30) & 0xff
    if k == ord('q'):
        break



#################
#   CLEANING    #
#################
log.flush()
log.close()
cap.release()
out.release()
out2.release()
cv.destroyAllWindows()
