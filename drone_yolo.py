import numpy as np
import darknet
import cv2


def retbox(detections,i,frame) :
	label = detections[i][0].decode('utf-8')
	score = detections[i][1]
	classes = labels_arr.index(label)

	x1 = int(round((detections[i][2][0]) - (detections[i][2][2]/2.0))) # top left x1 
	y1 = int(round((detections[i][2][1]) - (detections[i][2][3]/2.0))) # top left xy 
	x2 = int(round((detections[i][2][0]) + (detections[i][2][2]/2.0))) # bottom right x2 
	y2 = int(round((detections[i][2][1]) + (detections[i][2][3]/2.0))) # bottom right y2 
                
	box = np.array([x1,y1,x2,y2])

	return label, score, box

def pizza_status(y1,y2,frame) :
	if y2 > frame.shape[0]*14/20 :
		#pull
		status = 'pull'
		line_color_b = (0,0,255)
		txt_color = (0,0,255)
        
	elif y1 < frame.shape[0]*6/20 :
		#push
		status = 'push'
		line_color_f = (0,0,255)
		txt_color = (0,0,255)
        
	elif y2 < frame.shape[0]*14/20 and x1 > rgb_img.shape[0]*6/20 :
		#ok
		status = 'ok'
		txt_color = (0,255,0)

	return status,line_color_f,line_color_b,txt_color


cap = cv2.VideoCapture(0)
threshold = 0.9

stauts = ''
line_color_f,line_color_b,txt_color = (0,255,0),(0,255,0),(0,255,0)

while True:
	ret, frame = cap.read()
	detections = darknet.detect_image(net,meta, frame , thresh=.15)
    
	for i in range(len(detections)) :
		label , score , box = retbox(detections,i,frame,labels_arr)
		left,top,right,bottom=box
		#-----Draw Bounding box-----
		#cv2.putText(frame, label, (x1,y1), cv2.FONT_HERSHEY_SIMPLEX, 2, rgb, 3)
		#cv2.rectangle(frame, (x1,y1), (x2,y2), rgb, 3)
		#---------------------------
		if label == 'pizza' :
			status,line_color_f,line_color_b,txt_color = pizza_status(top,bottom,frame)
        
	cv2.putText(frame, status, (100,50), cv2.FONT_HERSHEY_SIMPLEX, 2, txt_color, 3)
	cv2.line(frame,(int(frame.shape[0]*6/20),0),(int(frame.shape[1]*6/20),frame.shape[0]),line_color_f,2)
	cv2.line(frame,(int(frame.shape[0]*14/20),0),(int(frame.shape[1]*14/20),frame.shape[0]),line_color_b,2)
	cv2.imshow('frame',frame)
	k = cv2.waitKey(1)
	if k == 27 :
		break

cv2.destroyAllWindows()
cap.release()
