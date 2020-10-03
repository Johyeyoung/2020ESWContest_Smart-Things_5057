#!/usr/bin/env python
# -*- coding: utf-8 -*-
from geometry_msgs.msg import Twist
from tf.transformations import euler_from_quaternion, quaternion_from_euler
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
import rospy, math, json, time
from std_msgs.msg import String
from Lidar import Lidar
from mqtt_subscribe import Mqtt_subscribe


class Motion:
    def __init__(self):
        self.LINEAR = 0.1

        self.roll = pitch = yaw = 0.0
        self.current_degree = 0
        self.position_x = 0
        self.position_y = 0
        self.kp = 0.3
        self.receive_order = ""
        self.avg = []
        self.front = 0

        rospy.init_node('rotate_robot')

        # mqtt 서브스크라이브 함
        # Mqtt_subscribe init 코드 보면댐
        # otp 토픽 받는 서브스크라이브임
        self.otp_subscribe = Mqtt_subscribe('/otp_start')
        # 경로 토픽 받는 서브스크라이브임
        self.path_subscribe = Mqtt_subscribe('/test')
        # # 이거는 경로를 출력함,..
        # self.path = self.path_subscribe.get_topic_data()
        # # start 함수에.. 경로를 집어넣으삼
        # self.start(self.path)


        self.odom_sub = rospy.Subscriber('/odom', Odometry, self.orientation_callback)
        self.sub_lds = Lidar('scan')
        # 이녀석은 get_front받음..
        self.front = self.sub_lds.get_front()
        


        self.ack_publisher = rospy.Publisher('cmd_vel', Twist, queue_size=10)
        self.r = rospy.Rate(50)
        self.command = Twist()
        rospy.sleep(2)

        self.recieve_order = "G75/R44"
        self.order = self.receive_order.split("/")
        ###################
        ###################
        self.start(self.order)
        rospy.spin()

    # 터틀봇의 움직임을 받음
    def orientation_callback(self, msg):
        orientation_q = msg.pose.pose.orientation
        self.position_x = msg.pose.pose.position.x
        self.position_y = msg.pose.pose.position.y
        orientation_list = [orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w]
        self.roll, self.pitch, self.yaw = euler_from_quaternion(orientation_list)


    def move(self, linear, angular):
        twist = Twist()
        twist.linear.x = linear
        twist.angular.z = angular
        self.ack_publisher.publish(twist)

        # 터틀봇 기본 동작

    def start(self, order):
        print(order)
        min_move = 0
        # 터틀봇 움직임의 최소 단위
        for i in range(len(order)):
            if order[i][0] == 'R':  # 오른쪽으로 회전
                self.move_right(float(order[i][1:]))
            elif order[i][0] == 'L':  # 왼쪽으로 회전
                self.move_left(float(order[i][1:]))
            elif order[i][0] == 'G':  # 앞으로 이동
                print("okay_1")
                print(int(order[i][1:]))
                self.move_front(float(order[i][1:]))
            elif order[i][0] == 'B':  # 뒤로 이동
                self.move_back(float(order[i][1:]))

    def lds_move(self, dis):
        print("okay_2")

        dis = dis / 100
        print(dis)
        print(type(dis))
        current_front = self.front
        time.sleep(0.1)
        print(current_front)
        while not rospy.is_shutdown():
            time.sleep(0.01)
            self.move(0.05, 0)
            print("no")

            if self.front - current_front < -1 * 1.5 * dis:
                continue

            if self.front - current_front <= -1 * dis:
                print(self.front - current_front)
                time.sleep(0.1)
                self.move(0, 0)
                print("done")
                break

    def move_front(self):
        self.current_degree = 0

        while not rospy.is_shutdown():
            # quat = quaternion_from_euler (roll, pitch,yaw)
            # print quat
            target_rad = 0 * math.pi / 180
            self.command.angular.z = self.kp * (target_rad - self.yaw)
            self.ack_publisher.publish(self.command)
            print("-------")
            print("taeget={} current:{}", self.current_degree, self.yaw)
            print(self.command.angular.z)
            print("------")
            self.r.sleep()
            if (int(self.command.angular.z * 100) == 0):
                break
        print(dis)
        print(type(dis))
        self.lds_move(dis)

    def move_back(self, dis):  # 180 방향으로 회
        self.current_degree = 180

        while not rospy.is_shutdown():
            # quat = quaternion_from_euler (roll, pitch,yaw)
            # print quat
            target_rad = 180 * math.pi / 180
            self.command.angular.z = self.kp * (target_rad - self.yaw)
            self.ack_publisher.publish(self.command)
            print("taeget={} current:{}", self.current_degree, self.yaw)
            print(self.command.angular.z)
            self.r.sleep()
            if (int(self.command.angular.z * 100) == 0):
                break
        self.lds_move(dis
    def move_right(self, dis):
        self.current_degree = 180

        while not rospy.is_shutdown():
            # quat = quaternion_from_euler (roll, pitch,yaw)
            # print quat
            target_rad = 180 * math.pi / 180
            self.command.angular.z = self.kp * (target_rad - self.yaw)
            self.ack_publisher.publish(self.command)
            print("taeget={} current:{}", self.current_degree, self.yaw)
            print(self.command.angular.z)
            self.r.sleep()
            if (int(self.command.angular.z * 100) == 0):
                break
        self.lds_move(dis)

    def move_stop(self):  # 정지
        self.move(0, 0)

    def move_left(self, dis):  # 90도 방향으로 회전
        self.current_degree = 90
        while not rospy.is_shutdown():
            # quat = quaternion_from_euler (roll, pitch,yaw)
            # print quat
            target_rad = 90 * math.pi / 180
            self.command.angular.z = self.kp * (target_rad - yaw)
            self.ack_publisher.publish(self.command)
            print("taeget={} current:{}", self.current_degree, yaw)
            print(self.command.angular.z)
            self.r.sleep()
            if (int(self.command.angular.z * 100) == 0):
                break
        self.lds_move(dis)

if __name__ == '__main__':
    turtlebot = Motion()