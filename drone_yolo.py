import numpy as np
import time
import cv2
import imutils
from imutils.video import FPS
from imutils.video import VideoStream
from DRONE_Client import *


LABELS_FILE = './yolo/obj.names'
CONFIG_FILE = './yolo/yolov4-tiny-custom.cfg'
WEIGHTS_FILE = './yolo/yolov4-tiny-custom_3000.weights'
CONFIDENCE_THRESHOLD = 0.9
H, W = None, None
fps = FPS().start()
LABELS = open(LABELS_FILE).read().strip().split("\n")
np.random.seed(4)
COLORS = np.random.randint(0, 255, size=(len(LABELS), 3),dtype="uint8")
net = cv2.dnn.readNetFromDarknet(CONFIG_FILE, WEIGHTS_FILE)


# determine only the *output* layer names that we need from YOLO
ln = net.getLayerNames()
ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]

############# Drone 에서 이미지를 받아서 전송하는 부분 ################
# ....... 1st : 서버와 연결
TCP_IP = '192.168.0.66'
TCP_PORT = 5009
drone_client = DRONE_Client(TCP_IP, TCP_PORT)

# ....... 2nd : 서버에 이미지 전송 시도
successFrame = 0
# vs = cv2.VideoCapture("demo.mp4")
vs = cv2.VideoCapture("rtsp://192.168.10.2:8554/test")

while vs.isOpened:
	try:
		_, image = vs.read()

		# 이미지 사이즈 읽어들이기
		if W is None or H is None:
			H, W = image.shape[:2]

		blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB=True, crop=False)
		net.setInput(blob)
		layerOutputs = net.forward(ln)

		# initialize our lists of detected bounding boxes, confidences, and
		# class IDs, respectively
		boxes = []
		confidences = []
		classIDs = []

		# loop over each of the layer outputs
		for output in layerOutputs:
			# loop over each of the detections
			for detection in output:
				# extract the class ID and confidence (i.e., probability) of
				# the current object detection
				scores = detection[5:]
				classID = np.argmax(scores)
				confidence = scores[classID]

				# filter out weak predictions by ensuring the detected
				# probability is greater than the minimum probability
				if confidence > CONFIDENCE_THRESHOLD:
					# scale the bounding box coordinates back relative to the
					# size of the image, keeping in mind that YOLO actually
					# returns the center (x, y)-coordinates of the bounding
					# box followed by the boxes' width and height
					box = detection[0:4] * np.array([W, H, W, H])
					(centerX, centerY, width, height) = box.astype("int")

					# use the center (x, y)-coordinates to derive the top and
					# and left corner of the bounding box
					x = int(centerX - (width / 2))
					y = int(centerY - (height / 2))

					# update our list of bounding box coordinates, confidences,
					# and class IDs
					boxes.append([x, y, int(width), int(height)])
					confidences.append(float(confidence))
					classIDs.append(classID)

		# apply non-maxima suppression to suppress weak, overlapping bounding
		# boxes
		idxs = cv2.dnn.NMSBoxes(boxes, confidences, CONFIDENCE_THRESHOLD,
								CONFIDENCE_THRESHOLD)

		# ensure at least one detection exists
		if len(idxs) > 0:
			img_tmp = image
			# loop over the indexes we are keeping
			for i in idxs.flatten():
				# extract the bounding box coordinates
				(x, y) = (boxes[i][0], boxes[i][1])
				(w, h) = (boxes[i][2], boxes[i][3])

				color = [int(c) for c in COLORS[classIDs[i]]]

				cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
				text = "{}: {:.4f}".format(LABELS[classIDs[i]], confidences[i])
				cv2.putText(image, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

			# ....... 3rd : 이미지에 전체 맵이 담았는지 판단 - 이미지 & 객체 위치
			correctMap = drone_client.fullMapChecker(img_tmp)

			# ....... 4th : 이미지가 전체 맵을 담았다고 판단되면 서버에 전송
			if correctMap:
				print("sending")
				cv2.imwrite("test.jpg", cv2.resize(img_tmp, (800, 600)))
				drone_client.sendToServer(image, (x + w//2, y + h//2))
				successFrame += 1


		# ....... 5th : 보낸 이미지가 3장이면 소켓 연결 끊고 탈출
		if successFrame == 8:
			drone_client.sockClose()


		fps.update()

		# show the output image
		cv2.imshow("output", cv2.resize(image, (800, 600)))
		if cv2.waitKey(1) & 0xFF == ord("q"):
			break

	except:
		break


fps.stop()

print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
cv2.destroyAllWindows()

# release the file pointers
print("[INFO] cleaning up...")
vs.release()
