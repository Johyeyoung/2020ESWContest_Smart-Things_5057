#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy
from std_msgs.msg import String


class Mqtt_subscribe:

    def __init__(self, topic):
        self.receive_data = '_'
        rospy.Subscribe(topic, String, self.read_topic_data)

    def read_topic_data(self, data):
        print('data from mqtt')
        self.receive_data = data.data
        print(self.receive_data)
        print('mqtt topic 받음')

    def get_topic_data(self):
        return self.receive_data
k