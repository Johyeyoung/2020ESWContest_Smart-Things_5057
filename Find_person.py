import cv2

# 터틀봇 영상 가져오기
cap = cv2.VideoCapture('http://192.168.0.32:8080/stream?topic=/usb_cam/image_raw')

while True:
   ret, frame = cap.read()
   cv2.imshow('original', frame)
   if cv2.waitKey(1) & 0xFF == ord('q'):
       break


