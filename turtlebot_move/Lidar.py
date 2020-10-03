#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
from sensor_msgs.msg import LaserScan


class Lidar:
    def __init__(self, topic):
        # 라이다 클래스 실행시 할거 쓰셈

        rospy.Subscribe(topic, LaserScan, self.callback_lidar)
        self.front = 0

    # 라이다 콜백 함수
    def callback_lidar(self, scan):
        Front = scan.ranges[0:14] + scan.ranges[345:359]
        Left1 = scan.ranges[15:34]
        Left2 = scan.ranges[35:54]
        Left3 = scan.ranges[55:74]
        Left4 = scan.ranges[75:94]
        Right1 = scan.ranges[325:344]
        Right2 = scan.ranges[305:324]
        Right3 = scan.ranges[285:304]
        Right4 = scan.ranges[265:284]
        back = scan.ranges[95:264]

        # average
        Front_avg = self.avge(Front)
        Left1_avg = self.avge(Left1)
        Left2_avg = self.avge(Left2)
        Left3_avg = self.avge(Left3)
        Left4_avg = self.avge(Left4)
        Right1_avg = self.avge(Right1)
        Right2_avg = self.avge(Right2)
        Right3_avg = self.avge(Right3)
        Right4_avg = self.avge(Right4)
        back_avg = self.avge(back)

        self.avg = [Front_avg, Left1_avg, Left2_avg, Left3_avg, Left4_avg, Right1_avg, Right2_avg, Right3_avg,
                    Right4_avg,
                    back_avg]

        self.front = scan.ranges[0]

    # lider값 평균 구하기
    def avge(self, arr):
        l = []
        for i in arr:
            if i == float("inf"):
                continue
            elif i == 0:
                continue
            else:
                l.append(i)
        # print(l)
        return sum(l) / (len(l) + 0.01)

    def get_front(self):
        return self.front
