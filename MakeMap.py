import cv2
import numpy as np

class Make_Map:
    def __init__(self, img=None):
        self.img = img
        self.img = cv2.resize(self.img, dsize=(400, 400), interpolation=cv2.INTER_AREA)
        #self.img = cv2.imread('./container/origin_state.jpg')

        # 이미지의 기본 속성 (행, 열, channel 정보)
        self.img_row = self.img.shape[0]  # 행 y
        self.img_cal = self.img.shape[1]  # 열 x

        self.canny = self.img.copy()
        self.imgray = self.img.copy()
        self.cut_img = self.img.copy()

        self.img_result = self.img.copy()


    def get_Max_contour(self):

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

        # 사각형의 테두리가 그어진 그림으로 다시 등고선 처리하기
        imgray = cv2.GaussianBlur(self.cut_img, (5, 5), 0)
        imgray = cv2.cvtColor(imgray, cv2.COLOR_BGR2GRAY)
        self.canny = cv2.Canny(imgray, 100, 200)




    ################## 휘어진 사진 보정하기 1 ##########################
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
        #print("LeftTop: {}, LeftBottom: {}, RightTop: {}, RightBottom: {}".format(rect[0], rect[3], rect[1], rect[2]))
        return rect

    ################## 휘어진 사진 보정하기 2 ##########################
    def delete_destroy(self):
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
        cv2.imshow("img_result1", self.img_result)
        cv2.imshow("img_result0", self.img)
        cv2.waitKey(0)


    ########## 밀반입자의 위치를 반환################
    def find_target_location(self):
        self.img_result2 = cv2.resize(self.img_result, (150, 150))
        imgray = cv2.GaussianBlur(self.img_result2, (5, 5), 0)
        imgray = cv2.cvtColor(imgray, cv2.COLOR_BGR2GRAY)
        canny = cv2.Canny(imgray, 100, 200)
        x, y = 75, 75
        target_cndt = []
        contours, hierarchy = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            area = cv2.contourArea(cnt)
            #print("area", area)
            epsilon = 0.02 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            #print(len(approx))
            if len(approx) > 5 and 30 > area > 12:
                print(len(approx), "area:", area)
                area = cv2.contourArea(cnt)
                x, y, w, h = cv2.boundingRect(cnt)
                cx, cy = x + w//2, y + h//2
                target_cndt.append((area, cx, cy))
                cv2.drawContours(self.img_result2, [approx], 0, (0, 1, 9), 2)
        if target_cndt:
            target_cndt = sorted(target_cndt, key=lambda x: x[0], reverse=True)
            print(target_cndt)
            x, y = target_cndt[0][1], target_cndt[0][2]
            cv2.line(self.img_result2, (x, y), (x, y), (0, 225, 225), 2)


        print("target:", round(y/10), round(x/10))
        return round(x/10), round(y/10)



    def make_contour(self):
        imgray = cv2.cvtColor(self.img_result, cv2.COLOR_BGR2GRAY)
        for i in range(4, imgray.shape[0]):
            for j in range(4, imgray.shape[1]):
                if imgray[i, j] > 90:
                    imgray[i, j] = 255
                else: imgray[i, j] = 0

        #imgray = cv2.GaussianBlur(imgray, (5, 5), 0)
        self.canny = cv2.Canny(imgray, 100, 200)

        # 등고선 전처리 ('contours'는 리스트로써 각각의 등고선들(등고선도 리스트로 각각의 점을 담음)을 담고있다)
        contours, hierarchy = cv2.findContours(self.canny, cv2.RETR_EXTERNAL,
                                               cv2.CHAIN_APPROX_SIMPLE)
        for i in range(0, len(contours)):
            cnt = contours[i]
            epsilon = 0.005 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            size = len(approx)

            # x좌표만 담아오기  - approx의 좌표를 이용
            x_list = []
            for i in range(len(approx)):
                col_1 = approx[i][:, 0]
                x_list.append(int(col_1))
            #print(x_list)






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
        #print("after:", list)


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
        #################중간 결과 좌표###################################################
        for i in range(self.img_result.shape[0]):  # 행 y
            result = ''
            for j in range(self.img_result.shape[1]):
                if self.canny[i, j] == 255:
                    self.canny[i, j] = 7
                result += str(self.canny[i, j])

        dic_int7 = []    # x 좌표 얻기
        for j in range(self.img_result.shape[1]):  # 열 x
            int7 = 0  # 컨테이너
            for i in range(self.img_result.shape[0]):  # 행 y
                if self.canny[i, j] == 7:
                    int7 += 1
            dic_int7.append(int7)
        #print("dic_int7:", dic_int7)

        x_dot = self.get_dot(dic_int7)
        x_dot.append(self.img_result.shape[1])
        #print("x_dox:", x_dot)


        row_dic_int7 = []   # ↓ y 좌표 얻기
        for i in range(self.img_result.shape[0]):
            int7 = 0
            for j in range(self.img_result.shape[1]):
                if self.canny[i, j] == 7:
                    int7 += 1
            row_dic_int7.append(int7)
        #print("row_dic_int7:", row_dic_int7)
        y_dot = self.get_dot(row_dic_int7)
        y_dot.append(self.img_result.shape[0])
        #print("y_dox:", y_dot)
        for x in x_dot:
            cv2.line(self.img_result, (x, 0), (x, self.img_result.shape[0]), (0, 225, 225), 2)
        for y in y_dot:
            cv2.line(self.img_result, (0, y), (self.img_result.shape[1], y), (0, 225, 225), 2)
        ########### 앞서 구한 픽셀 값을 이용해 GrayScale의 값이 일정 수준이 이상은 컨테이너 영역으로
        imm = cv2.cvtColor(self.img_result, cv2.COLOR_BGR2GRAY)
        for i in range(len(y_dot)):
            for j in range(len(x_dot)):
                if i < len(y_dot)-1 and j < len(x_dot)-1:
                    # 무게중심구하기
                    y_gap = y_dot[i+1] - y_dot[i]
                    x_gap = x_dot[j+1] - x_dot[j]
                    cX, cY = abs(int(x_dot[j] + x_gap / 2)), abs(int(y_dot[i] + y_gap / 2))
                    cv2.line(self.img_result, (cX, cY), (cX, cY), (255, 0, 255), 4)
                    if 90 <= imm[cY, cX] <= 255:
                        # 보드판은 검정 사각형으로 그림그리기
                        cv2.rectangle(self.img_result, (x_dot[j], y_dot[i]), (x_dot[j+1], y_dot[i+1]), (0, 0, 0), -1)



############## 최종 결과 맵 ################
    def draw_result_map(self):

        self.make_contour()
        self.pixel_content()
        # 한 픽셀에 해당하는 실제거리 구하기
        real_width = 150  # 맵의 한면: 150cm
        picture_width = self.img_result.shape[0]  # 맵의 한면
        one_pixel = real_width/picture_width  # 하나의 픽셀이 담당하는 실제거리
        print('한픽셀에 해당하는 실제 거리(cm):', one_pixel)
        self.img_result = cv2.resize(self.img_result, (150, 150))

        # 자른 이미지들 저장 경로 및 저장
        cv2.imwrite('./container/map.jpg', self.img_result)
        #cv2.imshow("result_2", self.img_result)
        #cv2.waitKey(0)

        # 맵의 오차범위를 줄이기 위해 터틀봇이 이동할 수 있는 칸의 크기로 0.1배수 줄여준다
        self.img_result = cv2.resize(self.img_result, None, fx=0.1, fy=0.1, interpolation=cv2.INTER_AREA)

        ############## 맵 그리기 -보드판(도로) = 0 / 컨테이너 != 0 ################
        line_info = []
        line_info_str = []
        self.result_imgray = cv2.cvtColor(self.img_result, cv2.COLOR_BGR2GRAY)
        for i in range(self.img_result.shape[0]):
            drawing = ''
            for j in range(self.img_result.shape[1]):
                if self.result_imgray[i, j] != 0:  # 보드판이 아닌 컨테이너면
                    self.result_imgray[i, j] = 1
                drawing += str(self.result_imgray[i, j])
            line_info_str.append(drawing)
            print(drawing)
            drawing = list(drawing)
            drawing = list(map(int, drawing))
            line_info.append(drawing)


        return line_info

if __name__ =='__main__':
    img = cv2.imread('./container/origin.jpg')
    realize = Make_Map(img)
    realize.get_Max_contour()
    realize.delete_destroy()
    realize.find_target_location()
    realize.draw_result_map()
