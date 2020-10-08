#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
import time
from move import Turtlebot_move

if __name__ == '__main__':

order = ""

time.sleep(2)
move = Turtlebot_move()
while not rospy.is_shutdown():
    while move.mqtt_sub.get_recive_order() == "":  # 서버로부터 경로를 받을떄까지 기다림
        print("waiting reived_order")

    recive_order = move.mqtt_sub.get_recive_order()  # 경로를 임의로 설정
    order = recive_order.split("/")  # "/" 기준으로 명령을 분리
    move.start(order)  # 터틀봇 이동 시작

    # 경로 이동후 OTP확인
    if (move.mqtt_sub.get_otp_flag() == "start"):  # 목표물을 발견했을 경우 OTP인증 요구
        move.mqtt_sub.otp_start()  # 인증 요구후 실패 성공 상관 없이 원래 경로로 복귀
        order = order + ["G0"]
        order = move.order_reversed(order)  # 경로를 역순으로 정렬
        move.start(order)  # 역순으로 정렬된 경로로 이동
        break

    elif (move.mqtt_sub.get_otp_flag() == "lost"):  # 목표물을 발견하지 못했을 경우 서버에 알림
        move.mqtt_sub.otp_lost()  # 알리고 그 자리에서 다음 명령 대기
        continue




