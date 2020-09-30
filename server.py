import socket
import cv2
import numpy
from Find_path import *
from MongoDB import *
import warnings
import Find_person

warnings.simplefilter("ignore", DeprecationWarning)

#socket 수신 버퍼를 읽어서 반환하는 함수
def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

#수신에 사용될 내 ip와 내 port번호
TCP_IP = '192.168.0.15'
TCP_PORT = 5009

#TCP소켓 열고 수신 대기
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(True)
print("_________ SERVER is waiting _________")
conn, addr = s.accept()
print("_________ SERVER get Data _________")

#String형의 이미지를 수신받아서 이미지로 변환 하고 화면에 출력
length = recvall(conn, 16) #길이 16의 데이터를 먼저 수신하는 것은 여기에 이미지의 길이를 먼저 받아서 이미지를 받을 때 편리하려고 하는 것이다.
stringData = recvall(conn, int(length))
data = numpy.fromstring(stringData, dtype='uint8')
s.close()  #................이부분 닫지 말까
decimg = cv2.imdecode(data, 1)

# 이미지 확인하기
#cv2.imshow('SERVER', decimg)
#cv2.waitKey(0)
#cv2.destroyAllWindows()

# ...... 0. mongoDB에 저장할 객체 생성
mongo = MongoDB()  # mongoDB 객체 생성


# ...... 1. save origin image from drone
cv2.imwrite('./container/origin.jpg', decimg)
img = open('./container/origin.jpg', 'rb')
mongo.storeImg_map(img, 'map_origin.jpg')
print("Drone image save!!")


# ...... 2. 길찾기 시작 및 맵 DB에 저장
print("____________find_path_____________")
# drone이 넘겨준 이미지를 이용하여 길찾기 알고리즘
# decimg = cv2.imread('./container/origin.jpg')
find_path = Find_path(decimg)
find_path.bfs()
find_path.real_path()




# Read Turtlebot wabCam and find person
Find_person.check_person()
