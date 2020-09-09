from MakeMap import * 
import cv2
from MongoDB import *

class Find_path:
    def __init__(self):
        # 객체 생성
        self.makeMap = Realize()
        self.target_x, self.target_y = self.makeMap.find_target_location()  # 밀입자의 좌표
        self.target_x, self.target_y = 32, 149  # 밀입자의 좌표
        self.map, self.map_str = self.makeMap.draw_result_map()  # 맵 만들기

        # check 맵 초기화
        self.check_map = [[0 for i in range(len(self.map[0]))] for row in range(len(self.map[0]))]
        self.arrow = {(0, 1): "→",  (1, 0): "↓", (0, -1): "←", (-1, 0): "↑"}  # (y, x)

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

    def real_path(self):
        img = cv2.imread("./container/map.jpg")
        for p in range(len(self.path)):
            x, y = self.path[p][0], self.path[p][1]
            #self.map_str[y] = self.map_str[y][:x-1] + self.arrows[p] + self.map_str[y][x+1:]
            cv2.line(img, (x, y), (x, y), (255, 0, 255), 2)
        self.target_x, self.target_y = 32, 149  # 밀입자의 좌표
        cv2.line(img, (self.target_x, self.target_y), (self.target_x, self.target_y), (255, 0, 255), 5)

        cv2.imshow('test', img)
        cv2.waitKey(0)

        # mongoDB로 옮기기 1......자른 이미지들 저장 경로 및 저장
        cv2.imwrite('./container/map_result.jpg', img)
        img = open('./container/map_result.jpg', 'rb')
        self.mongo.storeImg(img, 'map.jpg')  # 넘길 이미지와 이름

        # mongoDB로 옮기기 2.......좌표
        arrows = self.arrows.split('/')
        print(arrows)
        result = [[arrow[0], len(arrow)] for arrow in arrows]
        print(result)

        checked = {'→': -18, "↓": -18, "←": -18, "↑": -18}
        pos = ''
        for r in result:
            if checked[r[0]] < 0:
                checked[r[0]] += r[1]
                pos += r[0]
                pos += str(checked[r[0]])  # 방향
            else:
                pos += r[0]
                pos += str(r[1])

        import paho.mqtt.client as mqtt
        # MQTT client 생성, 이름 ""
        mqtt = mqtt.Client("loadFinder")
        mqtt.connect("localhost", 1883)  # 로컬호스트에 있는 MQTT서버에 접속
        mqtt.publish("mqtt/pathList", pos)  # topic 과 넘겨줄 값

if __name__ =='__main__':
    realize = Find_path()
    realize.bfs()
    realize.real_path()