# coding=utf-8
import cv2
import numpy as np
import matplotlib.pylab as plt
import seaborn as sns
import scipy as sp

class DeletDestroy:
    def __init__(self):
        self.img = cv2.imread('./container/16.jpg')
        self.img = cv2.resize(self.img, dsize=(400, 400), interpolation=cv2.INTER_AREA)

        # 이미지의 기본 속성 (행, 열, channel 정보)
        self.row = self.img.shape[0]  # 행 y
        self.cal = self.img.shape[1]  # 열 x

        self.canny = self.img.copy()
        self.imgray = self.img.copy()
        self.drawing_board = self.img.copy()  # 흰색으로만 이미지 그리기
        self.cut_img = self.img.copy()




class CreateMap:
    def __init__(self):
        self.img = cv2.imread('./container/16.jpg')
        self.img = cv2.resize(self.img, dsize=(400 , 400), interpolation=cv2.INTER_AREA)
        # 이미지의 기본 속성 (행, 열, channel 정보)
        self.row = self.img.shape[0]  # 행 y
        self.cal = self.img.shape[1]  # 열 x

        self.all_road = self.img.copy()  # 1차 컨투어처리 - 원본에 검정색 박스 그리기
        self.canny = self.img.copy()
        self.imgray = self.img.copy()
        self.img_result = self.img.copy()

        cv2.imshow('original', self.img)
        self.white_board = self.img.copy() # 2차 컨투어처리 - 흰공간에 검정색 박스 옮기기
        cv2.rectangle(self.white_board, (0, 0), (self.cal, self.row), (0, 0, 0), -1)  # 등고선 영역 검은색 사각형으로 채우기


        self.b_x, self.b_y, self.b_w, self.b_h = 0, 0, 0, 0

    def contour(self):
        # 1st: 데모판 영역따기 - findcontour 처리해서 가장 큰 사각형 잡기  -> 기울어짐 제거 작업
        imgray = cv2.GaussianBlur(self.img, (5, 5), 0)
        imgray = cv2.cvtColor(imgray, cv2.COLOR_BGR2GRAY)
        self.canny = cv2.Canny(imgray, 100, 200)

        # 등고선 전처리 ('contours'는 리스트로써 각각의 등고선들(등고선도 리스트로 각각의 점을 담음)을 담고있다)
        contours, hierarchy = cv2.findContours(self.canny, cv2.RETR_TREE,
                                               cv2.CHAIN_APPROX_SIMPLE)
        sorted_list = sorted(contours, key=lambda cc: len(cc))

        # 기울어진 최대사각형 "sorted_list[-1]" 을 원본이미지에 그린다
        self.hull = cv2.convexHull(sorted_list[-1])
        cv2.drawContours(self.img, [self.hull], 0, (0, 1, 9), 2)

        # 기울어지지 않은 최대사각형 - 이미지 자르기
        self.b_x, self.b_y, self.b_w, self.b_h = cv2.boundingRect(sorted_list[-1])
        # cv2.rectangle(self.img, (self.b_x, self.b_y), (self.b_x + self.b_w, self.b_h + self.b_y), (225, 0, 225),2)
        self.cut_img = self.img[self.b_y:self.b_h + self.b_y, self.b_x: self.b_x + self.b_w]

        #  칠판의 사이즈만들어주기 - 전체 색깔 검은색 + 사이즈도 줄여주기
        self.drawing_board = self.cut_img.copy()
        cv2.rectangle(self.drawing_board, (0, 0), (self.b_w, self.b_h), (0, 0, 0), -1)  # 검은색으로 채워주기

        # 사각형의 테두리가 그어진 그림으로 다시 등고선 처리하기
        imgray = cv2.GaussianBlur(self.cut_img, (5, 5), 0)
        imgray = cv2.cvtColor(imgray, cv2.COLOR_BGR2GRAY)
        self.canny = cv2.Canny(imgray, 100, 200)

        cv2.imshow('original', self.img)
        cv2.imshow('canny_result', self.canny)
        cv2.imshow('cutting', self.cut_img)
        cv2.waitKey(0)

    ################## 휘어진 사진 보정하기 1 ##########################
    def delet_destroy(self):
        # 꼭짓점 구하기
        rect = self.order_point(self.hull)
        (topLeft, topRight, bottomRight, bottomLeft) = rect

        # 가장 넓은 너비, 가장 긴 높이 구하기
        w1 = abs(bottomRight[0] - bottomLeft[0])
        w2 = abs(topRight[0] - topLeft[0])
        h1 = abs(topRight[1] - bottomRight[1])
        h2 = abs(topLeft[1] - bottomLeft[1])

        maxWidth = max([w1, w2])
        maxHeight = max([h1, h2])

        dst = np.float32([[0, 0], [maxWidth - 1, 0], [maxWidth - 1, maxHeight - 1], [0, maxHeight - 1]])
        M = cv2.getPerspectiveTransform(rect, dst)
        self.img_result = cv2.warpPerspective(self.img, M, (maxWidth, maxHeight))

        cv2.imshow("original2", self.img)
        cv2.imshow("img_result", self.img_result)
        cv2.waitKey(0)

    ################## 휘어진 사진 보정하기 2 ##########################
    def order_point(self, contour):  # 등고선 라인이 주어지면 -> 꼭짓점을 찾는다
        rect = np.zeros((4, 2), dtype="float32")
        # x + y 죄표의 합이 가장 작은건 원점에 가까운 leftTop, 가장 큰건 원점에서 가장 먼 rightBottom
        # s = 각 행당 (axis = 1) x + y의 값
        contour = contour.reshape(-1, 2)
        s = contour.sum(axis=1)
        rect[0] = contour[np.argmin(s)]  # x + y 합이 가장 작은건: LeftTop
        rect[2] = contour[np.argmax(s)]  # x + y 합이 가장 큰건: RightBottom

        # y - x의 값이 가장 크면 leftBottom, 가장 작으면 RightTop
        diff = np.diff(contour, axis=1)
        rect[1] = contour[np.argmin(diff)]  # y - x 값이 가장 작으면: RightTop
        rect[3] = contour[np.argmax(diff)]  # y - x 값이 가장 크면: leftBottom
        print(
            "LeftTop: {}, LeftBottom: {}, RightTop: {}, RightBottom: {}".format(rect[0], rect[3], rect[1], rect[2]))
        return rect




    def demo_correct(self):
        self.imgray = cv2.cvtColor(self.img_result, cv2.COLOR_BGR2GRAY)
        for i in range(4, self.imgray.shape[0]):
            result = ''
            for j in range(4, self.imgray.shape[1]):
                if self.imgray[i, j] > 190:
                    self.imgray[i, j] = 255
                else:
                    self.imgray[i, j] = 0
                result += str(self.imgray[i, j])
            print(result)
        cv2.imshow('original222', self.imgray)
        self.imgray = cv2.Canny(self.imgray, 100, 200)
        contours, hierarchy = cv2.findContours(self.imgray, cv2.RETR_TREE,
                                               cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            cv2.drawContours(self.img_result, cnt, 0, (0, 1, 9), 2)

        cv2.imshow('original233', self.img_result)
        cv2.imshow('original2wewrwer33', self.imgray)

        cv2.waitKey(0)


    def correct(self):  # 사진 보정하기
        cv2.rectangle(self.imgray, (self.b_x, self.b_y), (self.b_x + self.b_w, self.b_h + self.b_y), (225, 0, 225),
                      1)  # 등고선 영역 검은색 사각형으로 채우기
        print("최대사각형", 'x = {}, y = {}, w = {}, h = {}'.format(self.b_x, self.b_y, self.b_w, self.b_h))

        road_width = {}
        for i in range(self.row):
            int67 = 0  # 컨테이버
            int0 = 0  # 도록
            checkMax = 0  # 최장 도로폭 구하기
            for j in range(self.cal):  # ->방향으로 검사
                if self.imgray[i, j] == 0:  # 도로부분
                    int0 += 1
                    checkMax += 1  # 가로 도로부분 중 최장 길이의 도로 구하기
                    # 컨테이너 부분인데 도로처럼 0으로 된거 컨테이너로 보이게 땜질하기
                    if i > 0 and j > 0 and self.imgray[i-1, j] != 0 and self.imgray[i, j-1] != 0:
                        self.imgray[i, j] = 99

                elif self.imgray[i, j] == 67:  # 컨테이너 부분
                    int67 += 1
                    if checkMax == 1:
                        self.imgray[i, j-1] = 67
                    if checkMax > 1 and checkMax not in road_width:
                        road_width[checkMax] = 1
                        checkMax = 0
                    elif checkMax > 1 and checkMax in road_width:
                        road_width[checkMax] += 1

        cv2.imshow("correct_img", self.imgray)


        real_width = int(input("실제 도로폭의 값을 입력해 주세요(cm):"))
        result = sorted(road_width.items(), key=lambda x: x[1], reverse=True)

        ########여기 다시 알고리즘짜야됨 도로폭에 해당하는 픽셀수###########
        picture_width = 32  # 도로 폭에 해당하는 픽셀수#################
        ############################################################

        one_pixel = real_width/ picture_width  # 하나의 픽셀이 담당하는 실제거리
        one_step = int(input("움직일 크기를 설정해주세요(cm):"))
        one_grid = round(one_step / one_pixel)  # 이제 좌표한칸에 해당하는 픽셀의 개수
        print('한픽셀에 해당하는 실제 거리:', one_pixel)
        print('좌표한칸에 해당하는 픽셀수:', one_grid)


        ###############맵 만들기#####################
        map = []  # 이차원 리스트
        for i in range(self.row):
            line_map = []  # 가로 한줄
            int0_count = 0  # 도로-일정크기의 픽셀에 해당할때까지
            int67_count = 0  # 컨테이너-일정크기의 픽셀에 해당될때까지
            for j in range(self.cal):
                if self.imgray[i, j] == 0:
                    if int67_count != 0 and int67_count > one_grid/2: # 미처 픽셀사이즈에 도달하지 못했는데 컨테이너 등장시 - 그동안 쌓아왔던거확인
                        line_map.append(1)
                        int67_count = 0
                    int0_count += 1
                    if int0_count == one_grid:
                        line_map.append(0)
                        int0_count = 0

                elif self.imgray[i, j] == 67:
                    if int0_count != 0 and int0_count > one_grid/2: # 미처 픽셀사이즈에 도달하지 못했는데 컨테이너 등장시 - 그동안 쌓아왔던거확인
                        line_map.append(0)
                        int0_count = 0
                    int67_count += 1
                    if int67_count == one_grid:
                        line_map.append(1)
                        int67_count = 0
            map.append(line_map)  # 이차원리스트에 리스트 넣기

        print(map)
        print(result)
        print(self.row, self.cal)

        cv2.line(self.imgray, (0, 0), (33, 0), 225, 5)


        cv2.waitKey(0)



    ##### 색깔로 메꾸는 방법 쓸데없음 ######
    def colorcheck(self):
        color = [57, 53, 209]  # 빨간색의 경우

        one_pixel = np.uint8([[color]])
        hsv = cv2.cvtColor(one_pixel, cv2.COLOR_BGR2HSV)
        hsv = hsv[0][0]

        # hsv 색공간에서 마우스 클릭으로 얻은 픽셀값과 유사한 픽셀값의 범위를 정합니다.
        if hsv[0] < 10:
            lower_blue1 = np.array([hsv[0] - 10 + 180, 30, 30])
            upper_blue1 = np.array([180, 255, 255])
            lower_blue2 = np.array([0, 30, 30])
            upper_blue2 = np.array([hsv[0], 255, 255])
            lower_blue3 = np.array([hsv[0], 30, 30])
            upper_blue3 = np.array([hsv[0] + 10, 255, 255])

        elif hsv[0] > 170:
            lower_blue1 = np.array([hsv[0], 30, 30])
            upper_blue1 = np.array([180, 255, 255])
            lower_blue2 = np.array([0, 30, 30])
            upper_blue2 = np.array([hsv[0] + 10 - 180, 255, 255])
            lower_blue3 = np.array([hsv[0] - 10, 30, 30])
            upper_blue3 = np.array([hsv[0], 255, 255])

        else:
            lower_blue1 = np.array([hsv[0], 30, 30])
            upper_blue1 = np.array([hsv[0] + 10, 255, 255])
            lower_blue2 = np.array([hsv[0] - 10, 30, 30])
            upper_blue2 = np.array([hsv[0], 255, 255])
            lower_blue3 = np.array([hsv[0] - 10, 30, 30])
            upper_blue3 = np.array([hsv[0], 255, 255])



        ######################## 여기서 부터는 원본 영상#########
        # 원본 영상을 HSV 영상으로 변환한다
        img_hsv = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV)

        # 범위 값으로 HSV 이미지에서 마스크를 생성합니다.
        img_mask1 = cv2.inRange(img_hsv, lower_blue1, upper_blue1)
        img_mask2 = cv2.inRange(img_hsv, lower_blue2, upper_blue2)
        img_mask3 = cv2.inRange(img_hsv, lower_blue3, upper_blue3)
        img_mask = img_mask1 | img_mask2 | img_mask3  # 이진화된 이미지 get

        # 마스크 이미지로 원본 이미지에서 범위값에 해당하는 영상 부분을 획득한다.
        img_result = cv2.bitwise_and(self.img, self.img, mask=img_mask)

        imgray = cv2.GaussianBlur(img_result, (5, 5), 0)
        imgray = cv2.cvtColor(imgray, cv2.COLOR_BGR2GRAY)
        thr = cv2.Canny(imgray, 10, 200)
        contours, hierarchy = cv2.findContours(img_mask, cv2.RETR_TREE,
                                               cv2.CHAIN_APPROX_SIMPLE)
        for i in range(len(contours)):
            # 각 등고선마다의 사각형 포인트를 구해, 일정 크기 이상의 사각형만을 반찬으로써 도출
            cnt = contours[i]
            # 기울어진 최대사각형 "sorted_list[-1]" 을 원본이미지에 그린다
            self.hull = cv2.convexHull(cnt)
            cv2.drawContours(self.all_road, [self.hull], 0, (0, 1, 9), 1)
            # x, y, w, h = cv2.boundingRect(cnt)
            # cv2.rectangle(self.all_road, (x, y), (x + w, h + y), (0, 1, 9), -1)

        cv2.imshow('findContour7', self.all_road)
        cv2.waitKey(0)

    def turnMode(self):
        img = cv2.imread("./container/17.jpg")
        imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        canny = cv2.Canny(imgray, 50, 1500, apertureSize=5, L2gradient=True)
        lines = cv2.HoughLinesP(canny, 0.8, np.pi / 180, 90, minLineLength=10, maxLineGap=100)

        contours, hierarchy = cv2.findContours(canny, cv2.RETR_TREE,
                                               cv2.CHAIN_APPROX_SIMPLE)
        sorted_list = sorted(contours, key=lambda cc: len(cc))
        # 기울어진 최대사각형 "sorted_list[-1]" 을 원본이미지에 그린다
        hull = cv2.convexHull(sorted_list[-1])
        cv2.drawContours(img, [hull], 0, (0, 1, 9), 2)

        for i in lines:
            cv2.line(img, (i[0][0], i[0][1]), (i[0][2], i[0][3]), (0, 0, 255), 2)



        cv2.imshow("canny", canny)
        cv2.imshow("res", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()




if __name__ == "__main__":
    map = CreateMap()
    map.contour()
    map.delet_destroy()
    ##map.contourImg()
    #map.colorcheck()
    #map.turnMode()
    map.demo_correct()