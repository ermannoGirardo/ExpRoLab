#!/usr/bin/env python

import roslib
import rospy
from exproblab_assignment_1.srv import *
import math

##dictionary of the rooms
rooms= {
				'Cluedo_Room' : [0,0] , 
				'Hall' : [0,-3] , 
				'Study' : [3,-3] , 
				'Library' : [3,-1] , 
				'Biliard_Room' : [3,1] , 
				'Conservatory' : [3,3] , 
				'Ballroom' : [0,3] ,
				'Kitchen' : [-3,3] ,
				'Dining_Room' : [-3,0] ,
				'Lounge' : [-3,-3]
				}

##assume robot's average velocity in m/s
avg_speed=1

def clbk_time_simulated(req):
	"""
	The function callback of time_to_move custom service
	Args:
			(TimeToWait) req: is the client request for computing the time composed by
			(string) from_room: the room where the robot is
			(string) to_room: the room where the robot wants to go
	Returns:
			(float32) time: the time needed to arrive in to_room
	"""
	global rooms, avg_speed
	from_pos=rooms[req.from_room]
	to_pos=rooms[req.to_room]
	##compute the  euclidian distance
	euc_dis=math.sqrt(pow(to_pos[0]-from_pos[0],2) + pow(to_pos[1]-from_pos[1],2))
	time=avg_speed * euc_dis
	a=TimeToWaitResponse()
	a.time=time
	return a


def main():
	"""
	Main funtion of the time_for_simulation node
	Initialize the node
	Declare a service time_to_move of type TimeToWait (custom service)
	Args:
			(string) from_room: the room where the robot is
			(string) to_room: the room where the robot wants to go
	Returns:
			(float32) time: is the time needed to arrive in to_room (assuming an average velocity of 1m/s)
	"""
	rospy.init_node('time_for_simulation')
	s=rospy.Service('time_to_move',TimeToWait,clbk_time_simulated)
	print('Ready to compute the time needed\n')
	rospy.spin()
	
	
if __name__ == '__main__' :
	main()
