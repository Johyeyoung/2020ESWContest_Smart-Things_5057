from MakeMap import *
import cv2
from MongoDB import *
import json

class Find_path:
    def __init__(self, img):
        # 1... map 생성자 객체 생성
        self.makeMap = Realize(img)
        # 2... map의 왜곡없애기
        self.makeMap.contour()
        self.makeMap.delete_destroy()
        # 4... 침입자의 위치 알아내기
        self.target_x, self.target_y = self.makeMap.find_target_location()  # 밀입자의 좌표
        # 3... 맵 만들기
        self.map, self.map_str = self.makeMap.draw_result_map()



        # check 맵 초기화
        self.check_map = [[0 for i in range(len(self.map[0]))] for row in range(len(self.map[0]))]
        self.arrow = {(0, 1): "R",  (1, 0): "G", (0, -1): "L", (-1, 0): "B"}  # (y, x)

        self.dx = [1, 0, -1, 0]
        self.dy = [0, 1, 0, -1]
        self.min = 1000000
        self.path = []
        self.arrows = ''

        # mongoDB 객체 생성
        self.mongo = MongoDB()



    def bfs(self):
        s = self.map
        dx = [1, -1, 0, 0]
        dy = [0, 0, -1, 1]
        queue = [[0, 0, [], []]]
        self.check_map[0][0] = 1

        while queue:
            x, y, path, direction = queue.pop(0)

            if x == self.target_x - 1 and y == self.target_y - 1:
                # 최종 경로 도착
                print(self.check_map[y][x])
                print("".join(direction))
                self.arrows = "".join(direction)
                self.path = path
                print(path)
                break

            for i in range(4):
                nx = x + dx[i]
                ny = y + dy[i]
                if 0 <= nx < self.target_x and 0 <= ny < self.target_y:
                    if self.check_map[ny][nx] == 0 and self.map[ny][nx] == 0:
                        self.check_map[ny][nx] = self.check_map[y][x] + 1
                        if direction and direction[-1] != self.arrow[(dy[i], dx[i])]:
                            queue.append((nx, ny, path+[(nx,ny)], direction + ['/', self.arrow[(dy[i], dx[i])]]))
                        else:
                            queue.append((nx, ny, path+[(nx,ny)], direction + [self.arrow[(dy[i], dx[i])]]))


    # 최적의 경로를 찾아서 mqtt로 보내고 경로가 담긴 이미지를 반환한다.
    def real_path(self):

        # 1.... 구해진 맵위에 turtlebot이 움직일 경로 그려주기
        img = cv2.imread("./container/map.jpg")
        for p in range(len(self.path)):
            x, y = self.path[p][0], self.path[p][1]
            cv2.line(img, (x, y), (x, y), (255, 0, 255), 2)
        cv2.line(img, (self.target_x, self.target_y), (self.target_x, self.target_y), (255, 255, 255), 5)

        # 2.... TurtleBot 에게 경로 정보 넘기기
        arrows = self.arrows.split('/')
        result = [[arrow[0], len(arrow)] for arrow in arrows]
        checked = {'R': -18, "G": -18, "L": -18, "B": -18}
        pos = ''
        for r in result:
            if checked[r[0]] < 0:
                checked[r[0]] += r[1]
                pos += r[0]
                pos += str(checked[r[0]])  # 방향
            else:
                pos += r[0]
                pos += str(r[1])
            pos += '/'
        print(pos)
        # .... TurtleBot 에게 경로 정보 넘기기
        import paho.mqtt.client as mqtt
        mqtt = mqtt.Client("loadFinder")  # MQTT client 생성, 이름 ""
        mqtt.connect("localhost", 1883)  # 로컬호스트에 있는 MQTT서버에 접속
        mqtt.publish("pathList", json.dumps({"data": pos}))  # topic 과 넘겨줄 값
        return img

if __name__ =='__main__':
    img = cv2.imread('./container/66.jpg')
    realize = Find_path(img)
    realize.bfs()
    img = realize.real_path()
    cv2.imshow('get_map', img)
    cv2.waitKey(0)