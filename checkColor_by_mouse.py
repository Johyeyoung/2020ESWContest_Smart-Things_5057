# coding=utf-8
import cv2
import numpy as np

hsv = 0
lower_blue1 = 0
upper_blue1 = 0
lower_blue2 = 0
upper_blue2 = 0
lower_blue3 = 0
upper_blue3 = 0


# 마우스 이벤트 생성
def mouse_callback(event, x, y, flags, param):
    global hsv, lower_blue1, upper_blue1, lower_blue2, upper_blue2, lower_blue3, upper_blue3

    # 마우스 왼쪽 버튼 누를 시 위치에 있는 픽셀값을 읽어와서 HSV로 변환한다.
    if event == cv2.EVENT_LBUTTONDOWN:

        imgray = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)
        print("gray", imgray[y, x])
        print(img_color[y, x])  # BGR 색상 추출하기
        color = img_color[y, x]



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
        #print("lower_blue1, upper_blue1, lower_blue2, upper_blue2, lower_blue3, upper_blue3")
        #print("mask:", lower_blue1, upper_blue1, lower_blue2, upper_blue2, lower_blue3, upper_blue3)


cv2.namedWindow('img_color')
cv2.setMouseCallback('img_color', mouse_callback)


while(True):
    img_color = cv2.imread('./container/0.4485609567901235.jpg')
    img_color = cv2.resize(img_color, dsize=(300, 300))

    # 원본 영상을 HSV 영상으로 변환한다
    img_hsv = cv2.cvtColor(img_color, cv2.COLOR_BGR2HSV)

    # 범위 값으로 HSV 이미지에서 마스크를 생성합니다.
    img_mask1 = cv2.inRange(img_hsv, lower_blue1, upper_blue1)
    img_mask2 = cv2.inRange(img_hsv, lower_blue2, upper_blue2)
    img_mask3 = cv2.inRange(img_hsv, lower_blue3, upper_blue3)
    img_mask = img_mask1 | img_mask2 | img_mask3  # 이진화된 이미지 get


    # 마스크 이미지로 원본 이미지에서 범위값에 해당하는 영상 부분을 획득한다.
    img_result = cv2.bitwise_and(img_color, img_color, mask=img_mask)




    # 등고선 처리하기
    img_result2 = img_color.copy()

    imgray = cv2.GaussianBlur(img_result, (5, 5), 0)
    imgray = cv2.cvtColor(imgray, cv2.COLOR_BGR2GRAY)
    thr = cv2.Canny(imgray, 10, 200)
    contours, hierarchy = cv2.findContours(img_mask, cv2.RETR_TREE,
                                           cv2.CHAIN_APPROX_SIMPLE)
    sorted_list = sorted(contours, key=lambda cc: len(cc))
    maxHull = cv2.convexHull(sorted_list[-1])
    cv2.drawContours(img_result2, [maxHull], 0, (225, 255, 255), 3)
    # for i in range(len(contours)):
    #
    #     # 각 등고선마다의 사각형 포인트를 구해, 일정 크기 이상의 사각형만을 반찬으로써 도출
    #     cnt = contours[i]
    #     x, y, w, h = cv2.boundingRect(cnt)
    #     hull = cv2.convexHull(cnt)
    #     cv2.drawContours(img_result2, [hull], 0, (0, 255, 0), 3)
    minLineLength = 70
    maxLineGap = 30



    cv2.imshow('img_color', img_color)
    cv2.imshow('img_result', img_result)

    cv2.imshow('img_result2', img_result2)


    # ESC 키누르면 종료
    if cv2.waitKey(1) & 0xFF == 27:
        break


cv2.destroyAllWindows()