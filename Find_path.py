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
        # 4... 침입자의 위치 알아내기
        self.target_x, self.target_y = math.ceil(location[0]/10), math.ceil(location[1] / 10)  # 밀입자의 좌표
        print("경로상의 침입자 위치:", self.target_x, self.target_y)
        #self.target_x, self.target_y = self.makeMap.find_target_location()  # 밀입자의 좌표
        # 3... 맵 만들기
        self.map = map

        # check 맵 초기화
        self.check_map = [[0 for i in range(len(self.map[0]))] for row in range(len(self.map[0]))]
        self.arrow = {(0, 1): "L",  (1, 0): "G", (0, -1): "R", (-1, 0): "B"}  # (y, x)

        self.arrows = ''

        # mongoDB 객체 생성
        self.mongo = MongoDB()


    # 최적의 경로를 찾는다
    def path_algorithm(self, postLocation):
        start_x, start_y = round(postLocation[0]/10), round(postLocation[1]/10)
        print("start_x:{}, start_y:{}".format(start_x+1, start_y+1))
        s = self.map
        dx = [1, -1, 0, 0]
        dy = [0, 0, -1, 1]
        queue = [[start_x, start_y, [], []]]
        self.check_map[start_y][start_x] = 1
<<<<<<< HEAD
        #print("destination", s[self.target_y - 1][self.target_x - 1])
        #print("destination2", s[start_y][start_x])
=======
        print("destination", s[self.target_y - 1][self.target_x - 1])
        print("destination2", s[start_y][start_x])
>>>>>>> f13faefe62aa05f3f3b9f6552c16dbc66d79aa54

        while queue:
            x, y, path, direction = queue.pop(0)

            if x == self.target_x - 1 and y == self.target_y - 1:
                # 최종 경로 도착
                print("".join(direction))
                self.arrows = "".join(direction)
                break

            for i in range(4):
                nx = x + dx[i]
                ny = y + dy[i]
                if 0 <= nx < 15 and 0 <= ny < 15:
                    if self.check_map[ny][nx] == 0 and self.map[ny][nx] == 0:
                        self.check_map[ny][nx] = self.check_map[y][x] + 1
                        if direction and direction[-1] != self.arrow[(dy[i], dx[i])]:
                            queue.append((nx, ny, path+[(nx,ny)], direction + ['/', self.arrow[(dy[i], dx[i])]]))
                        else:
                            queue.append((nx, ny, path+[(nx,ny)], direction + [self.arrow[(dy[i], dx[i])]]))



    # 구해진 최적의 경로를 mqtt로 보내고 경로가 담긴 이미지를 반환한다.
    def real_path(self):
        img = cv2.imread("./container/map.jpg")

        # 2.... TurtleBot 에게 경로 정보 넘기기
        if self.arrows:
            arrows = self.arrows.split('/')
            result = [a[0]+str(len(a)*10) for a in arrows]
            pos = '/'.join(result)
<<<<<<< HEAD
            print("!!!경로가 주어졌습니다!!! :", pos)
=======
            print(pos)
>>>>>>> f13faefe62aa05f3f3b9f6552c16dbc66d79aa54

            # 1.... 구해진 맵위에 turtlebot 이 움직일 경로 그려주기
            pos_lst = pos.split('/')
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
            return img, pos

        else:
            print("경로가 없습니다")



if __name__ =='__main__':
    img = cv2.imread('./container/origin.jpg')
    makeMap = Realize(img)
    makeMap.get_Max_contour()
    makeMap.delete_destroy()
    map = makeMap.draw_result_map()
    realize = Find_path(img, [80, 90], map)  # 인덱스 1부터 0부터 세지 말기
    realize.path_algorithm([140, 140])  # 시작점 인덱스 0부터
    img = realize.real_path()
