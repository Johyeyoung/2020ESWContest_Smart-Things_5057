# coding=utf-8
import cv2
import numpy as np
from matplotlib import pyplot as plt

class Realize:
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
        #cv2.rectangle(self.img, (self.b_x, self.b_y), (self.b_x + self.b_w, self.b_h + self.b_y), (225, 0, 225),2)
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

        dst = np.float32([[0, 0], [maxWidth-1, 0], [maxWidth-1, maxHeight-1], [0, maxHeight-1]])
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
        print("LeftTop: {}, LeftBottom: {}, RightTop: {}, RightBottom: {}".format(rect[0], rect[3], rect[1], rect[2]))
        return rect

    def make_contour(self):
        imgray = cv2.GaussianBlur(self.img_result, (5, 5), 0)
        imgray = cv2.cvtColor(imgray, cv2.COLOR_BGR2GRAY)
        self.canny = cv2.Canny(imgray, 100, 200)

        # 등고선 전처리 ('contours'는 리스트로써 각각의 등고선들(등고선도 리스트로 각각의 점을 담음)을 담고있다)
        contours, hierarchy = cv2.findContours(self.canny, cv2.RETR_EXTERNAL,
                                               cv2.CHAIN_APPROX_SIMPLE)
        for i in range(0, len(contours)):
            # 각 등고선마다의 사각형 포인트를 구해, 일정 크기 이상의 사각형만을 반찬으로써 도출
            cnt = contours[i]
            epsilon = 0.005 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            size = len(approx)

            # x좌표만 담아오기  - approx의 좌표를 이용
            x_list = []
            for i in range(len(approx)):
                col_1 = approx[i][:, 0]
                x_list.append(int(col_1))
            print(x_list)

            cv2.line(self.img_result, tuple(approx[0][0]), tuple(approx[size-1][0]), (225, 225, 0), 2)
            cv2.line(self.drawing_board, tuple(approx[0][0]), tuple(approx[size-1][0]), (225, 225, 0), 2)
            for k in range(size - 1):
                cv2.line(self.img_result, tuple(approx[k][0]), tuple(approx[k + 1][0]), (225, 225, 0), 2)
                cv2.line(self.drawing_board, tuple(approx[k][0]), tuple(approx[k + 1][0]), (225, 225, 0), 2)

                # x 좌표가 서로다른 점들을 분류했다 주어진 점들의 y 최대최소값으로 꼭짓점을 구하고 같은 y값은 잇는다
                if approx[k][0][0] < 50:
                    cv2.line(self.img_result, tuple(approx[k][0]), tuple(approx[k][0]), (225, 225, 0), 3)
                elif 50 < approx[k][0][0] < 90:
                    cv2.line(self.img_result, tuple(approx[k][0]), tuple(approx[k][0]), (225, 225, 225), 3)
                elif 90 < approx[k][0][0]:
                    cv2.line(self.img_result, tuple(approx[k][0]), tuple(approx[k][0]), (0, 225, 225), 3)
        cv2.imshow("board", self.drawing_board)
        cv2.imshow('test', self.canny)
        cv2.imshow('original3', self.img_result)
        cv2.waitKey(0)




    # 각 열이나 행에서 얻은 7의 개수에서 7의 수를 토대로 좌표리스트를 얻는다
    def get_dot(self, list):
        # 최빈값을 찾아서 사실은 그 아이들은 0임
        # 각 list 에 존재하는 숫자들이 빈도수를 딕셔너리로 저장한다 최대로 7이 많이 나온건 줄이 아니라 오차임 0으로 바꿔주기
        count_num = {}
        for i in set(list):
            count_num[i] = list.count(i)

        # value가 7개 이상이면 리스트에 담아둔다  0으로 변환시킬 숫자
        out_list = [key for key, value in count_num.items() if value > 10]

        # 해당 열을 0으로 바꾸고 열에서 발견된 7의 값도 0으로 change
        for i in range(len(list)):
            if list[i] < 2:  # 너무 작은 7의 개수는 그냥 오차임
                list[i] = 0
            elif list[i] in out_list:  # out_list 에 값이 있으면 0으로 변경한다
                list[i] = 0  # 0으로 값을 바꾸고


        # 0-숫자-0 -> 0-0-0으로   &&  숫자-0-숫자의 경우 -> 숫자-숫자-숫자
        for i in range(len(list)):
            if list[i] != 0 and list[i] < 10 and 0 < i < len(list) - 1 and list[i - 1] == 0 and list[i + 1] == 0:
                list[i] = 0
            if i < len(list) - 2 and list[i] != 0 and list[i + 1] == 0 and list[i + 2] != 0:
                list[i + 1] = list[i + 2]
        print("after:", list)


        # 연속된 0으로 이어지다가 숫자 군집이 나타나면 그 군집의 중앙값을 좌표로 저장한다
        dot_list = [0]  # 좌표리스트
        count = 0
        for i in range(len(list)):
            if i < len(list) - 1 and list[i] != 0:
                count += 1
            elif list[i] == 0 and count >= 1:
                dot_list.append(int(i - count/2))  # x의 중간 좌표를 추가한다
                count = 0
        return dot_list




    def pixel_content(self):

        #################최종 결과 좌표###################################################
        for i in range(self.img_result.shape[0]):  # 행 y
            result = ''
            for j in range(self.img_result.shape[1]):
                if self.canny[i, j] == 255:
                    self.canny[i, j] = 7
                result += str(self.canny[i, j])
            print(result)

        dic_int7 = []    # x 좌표 얻기
        for j in range(self.img_result.shape[1]):  # 열 x
            int7 = 0  # 컨테이너
            for i in range(self.img_result.shape[0]):  # 행 y
                if self.canny[i, j] == 7:
                    int7 += 1
            dic_int7.append(int7)
        print("dic_int7:", dic_int7)

        x_dot = self.get_dot(dic_int7)
        x_dot.append(self.img_result.shape[1])
        print("x_dox:", x_dot)


        row_dic_int7 = []   # ↓ y 좌표 얻기
        for i in range(self.img_result.shape[0]):
            int7 = 0
            for j in range(self.img_result.shape[1]):
                if self.canny[i, j] == 7:
                    int7 += 1
            row_dic_int7.append(int7)
        print("row_dic_int7:", row_dic_int7)
        y_dot = self.get_dot(row_dic_int7)
        y_dot.append(self.img_result.shape[0])
        print("y_dox:", y_dot)


        for x in x_dot:
            for i in range(self.img_result.shape[0]):
                cv2.line(self.img_result, (x, i), (x, i), (0, 225, 225), 2)
        for y in y_dot:
            for j in range(self.img_result.shape[1]):
                cv2.line(self.img_result, (j, y), (j, y), (0, 225, 225), 2)
        ###################################
        imm = cv2.cvtColor(self.img_result, cv2.COLOR_BGR2GRAY)
        for i in range(len(y_dot)):
            for j in range(len(x_dot)):
                if i < len(y_dot)-1 and j < len(x_dot)-1:
                    # 무게중심구하기
                    y_gap = y_dot[i+1] - y_dot[i]
                    x_gap = x_dot[j+1] - x_dot[j]
                    cX, cY = abs(int(x_dot[j] + x_gap / 2)), abs(int(y_dot[i] + y_gap / 2))
                    # 디버깅용
                    # print("y_dot[i]= {}, y_dot[i+1]= {}, x_dot[i] = {}, x_dot[i+1]= {}, cX={}, cY={}".format(y_dot[i], y_dot[i+1], x_dot[j], x_dot[j+1], cX, cY))

                    cv2.line(self.img_result, (cX, cY), (cX, cY), (255, 0, 255), 4)
                    if 170 <= imm[cY, cX] <= 220:
                        # 보드판은 사각형으로 그림그리기
                        cv2.rectangle(self.img_result, (x_dot[j], y_dot[i]), (x_dot[j+1], y_dot[i+1]), (0, 0, 0), -1)
                        #print("보드판:", imm[cY, cX])
                    else:
                        pass
                        #print("구분불가:", imm[cY, cX])


        cv2.imshow("result_2", self.img_result)
        cv2.waitKey(0)


########## 밀반입자의 위치를 반환################
    def find_target_location(self):
        x = 0
        y = 0
        return x ,y

############## 마지막 맵 ################
    def draw_result_map(self):
        # 한 픽셀에 해당하는 실제거리 구하기
        real_width = 150  # 맵의 한면: 150cm
        picture_width = self.img_result.shape[0]  # 맵의 한면
        one_pixel = real_width/picture_width  # 하나의 픽셀이 담당하는 실제거리
        print('한픽셀에 해당하는 실제 거리(cm):', one_pixel)


        ############## 맵 그리기 -보드판(도로) = 0 / 컨테이너 != 0 ################
        self.result_imgray = cv2.cvtColor(self.img_result, cv2.COLOR_BGR2GRAY)
        for i in range(self.img_result.shape[0]):
            drawing = ''
            for j in range(self.img_result.shape[1]):
                if self.result_imgray[i, j] != 0:  # 보드판이 아닌 컨테이너면
                    self.result_imgray[i, j] = 1
                drawing += str(self.result_imgray[i, j])
            print(drawing)

        ############## target을 확인하여 길을 찾아가기 ##############
        target_x, target_y = self.find_target_location()
        for j in range(self.img_result.shape[1]):
            if self.result_imgray[target_x, j] == 1:  # 컨테이너면
                break




if __name__ =='__main__':
    realize = Realize()
    realize.contour()
    realize.delet_destroy()
    realize.make_contour()
    realize.pixel_content()
    realize.draw_result_map()
