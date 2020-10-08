from MakeMap import *
import cv2
from MongoDB import *
import math

class Find_path:
    def __init__(self, img, location=None, map=None):
        # 1... map 생성자 객체 생성
        self.makeMap = Realize(img)
        # 2... map의 왜곡없애기
        self.makeMap.get_Max_contour()
        self.makeMap.delete_destroy()
        # 4... 침입자의 위치 알아내기 (1/10배로 줄임)
        self.target_x, self.target_y = math.ceil(location[0]/10), math.ceil(location[1] / 10)
        # 3... 맵 만들기
        self.map = map

        # check 맵 초기화
        self.check_map = [[0 for i in range(len(self.map[0]))] for row in range(len(self.map[0]))]
        self.arrows = ''



    # 최적의 경로를 찾는다
    def path_algorithm(self, postLocation):
        # ........ Turtlebot 의 시작 위치
        start_x, start_y = math.ceil(postLocation[0]/10), math.ceil(postLocation[1]/10)

        # ....... 위치 데이터 : index = 1(목적지), index = 0(시작점)  : print문은 => index 1부터
        print("---------------------------------------------------------------")
        print("          침입자의 위치: (x, y) = ({}, {}) | 좌표값 = {}".format(self.target_x, self.target_y, self.map[self.target_y - 1][self.target_x - 1]))
        print("          터틀봇의 위치: (x, y) = ({}, {}) | 좌표값 = {}".format(start_x+1, start_y+1, self.map[start_y][start_x])) #
        print("---------------------------------------------------------------")

        # ....... 경로 algorithm 시작
        dot_name = {(0, 1): "L",  (1, 0): "G", (0, -1): "R", (-1, 0): "B"}  # (y, x)
        dx = [1, -1, 0, 0]
        dy = [0, 0, -1, 1]
        queue = [[start_x, start_y, [], []]]
        self.check_map[start_y][start_x] = 1

        while queue:
            x, y, path, direction = queue.pop(0)

            if x == self.target_x - 1 and y == self.target_y - 1:
                # 최종 경로 도착
                print("          원본 경로: ", "".join(direction))  # LLLRRRGGG
                self.arrows = "".join(direction)
                self.arrows = self.path_MQTT(self.arrows)  # 주어진 형식대로 MQTT 메세지 데이터 정리
                break

            for i in range(4):
                nx = x + dx[i]
                ny = y + dy[i]
                if 0 <= nx < 15 and 0 <= ny < 15:
                    if self.check_map[ny][nx] == 0 and self.map[ny][nx] == 0:
                        self.check_map[ny][nx] = self.check_map[y][x] + 1
                        if direction and direction[-1] != dot_name[(dy[i], dx[i])]:
                            queue.append((nx, ny, path+[(nx,ny)], direction + ['/', dot_name[(dy[i], dx[i])]]))
                        else:
                            queue.append((nx, ny, path+[(nx,ny)], direction + [dot_name[(dy[i], dx[i])]]))


    # ..........1. MQTT 에 발행할 경로 메세지 형태로 전처리 L40/R50/
    def path_MQTT(self, pathData):
        if pathData:
            # LLLLRRRRR -> L40R50
            result = [a[0]+str(len(a)*10) for a in pathData.split('/')]
            pathData = '/'.join(result)
            print("          최종 경로: ", pathData)
            print("-------------------------------------------------------------------")

            return pathData


    # ..........2. 최적의 경로를 저장되어 있던 맵위에 그려주기
    def drawing_path(self):
        if self.arrows:
            # 1... 저장된 맵의 image 를 load.
            img = cv2.imread("./container/map.jpg")

            # 2.... 구해진 맵위에 turtlebot 이 움직일 경로 그려주기
            pos_lst = self.arrows.split('/')
            x, y = 0, 0
            for i in pos_lst:
                post_x, post_y = x, y
                if i[0] == "G":
                    y += int(i[1:])
                elif i[0] == "B":
                    y -= int(i[1:])
                elif i[0] == "L":
                    x += int(i[1:])
                elif i[0] == "R":
                    x -= int(i[1:])
                cv2.line(img, (post_x, post_y), (x, y), (255, 0, 255), 2)
            return img, self.arrows

        else:
            print("주어진 경로가 없습니다")



if __name__ =='__main__':
    img = cv2.imread('./container/origin.jpg')
    makeMap = Realize(img)
    makeMap.get_Max_contour()
    makeMap.delete_destroy()
    map = makeMap.draw_result_map()
    realize = Find_path(img, [80, 90], map)  # 인덱스 1부터 0부터 세지 말기
    realize.path_algorithm([140, 140])  # 시작점 인덱스 0부터
    img, path = realize.drawing_path()
