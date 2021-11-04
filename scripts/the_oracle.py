#!/usr/bin/env python

import roslib
import rospy
from exproblab_assignment_1.srv import *
from armor_msgs.srv import * 
from armor_msgs.msg import * 
import random

##The oracle know the true hypotesis
##Global variables for indentify the true hypotesis
## Get the param and  set the global variables
who=None
where=None
what=None
who=rospy.get_param("/who")
where=rospy.get_param("/where")
what=rospy.get_param("/what")
who=str(who)
where=str(where)
what=str(what)

def clbk_convalidation(req):
	"""
	The function callback of  hypotesis_convalidation custom service
	Args:
			(ConvalidateHp) req: is the request made by the client composed of
			(string) who: is the killer that the robot has acquired
			(string) where: is the place that the robot has acquired
			(string) what: is the weapon that the robot has acquired
	Returns:
			(ConvalidateHpResponse) res: the resonse from the server composed by
			(bool) who: if the person is correct return True
			(bool) where: if the place is correct return True
			(bool) what: if the weapon is correct return True
	"""
	global who, where, what
	res=ConvalidateHpResponse()
	##Check all the three fields of the hypotesis
	if(req.who==who):
		res.who=True
	else:
		res.who=False
	if(req.where==where):
		res.where=True
	else:
		res.where=False
	if(req.what==what):
		res.what=True
	else:
		res.what=False
	return res


def  clbk_make_hint(req):
	"""
	Function callback of make_hint custom service
	Args:
			(MakeHp) req: the request of client composed by
			(string) arg: the type of hints that robot wants to acquire
	Returns:
			(string) hint: the instance of the argument requested 
	"""
	##fill the armor argument to ask a new instance
	rospy.wait_for_service('armor_interface_srv')
	armor_client=rospy.ServiceProxy('armor_interface_srv', ArmorDirective)
	armor_req=ArmorDirectiveReq()
	armor_req.client_name='cluedo_fsm'
	armor_req.reference_name='cluedo_ontology'
	armor_req.command = 'QUERY'
	armor_req.primary_command_spec = 'IND'
	armor_req.secondary_command_spec = 'CLASS'
	hint=MakeHpResponse()
	if(req.arg=='who'):
		armor_req.args = ['PERSON']
		armor_res=armor_client(armor_req).armor_response.queried_objects
		print(armor_res)
		killer=random.choice(armor_res)
		hint.hint=str(killer)
		return hint
	if(req.arg=='where'):
		armor_req.args = ['PLACE']
		armor_res=armor_client(armor_req).armor_response.queried_objects
		killer_room=random.choice(armor_res)
		hint.hint=killer_room
		return hint
	if(req.arg=='what'):
		armor_req.args = ['WEAPON']
		armor_res=armor_client(armor_req).armor_response.queried_objects
		killer_weapon=random.choice(armor_res)
		hint.hint=killer_weapon
		return hint




def main():
	"""
	Body of main function
	Initialization of check_hypothesis node
	Desclaration of hp_convalidation custom service
	Args:
			(ConvalidateHp) req: is the request made by the client composed of
			(string) who: is the killer that the robot has acquired
			(string) where: is the place that the robot has acquired
			(string) what: is the weapon that the robot has acquired
	Returns:
			(ConvalidateHpResponse) res: the resonse from the server composed by
			(bool) who: if the person is correct return True
			(bool) where: if the place is correct return True
			(bool) what: if the weapon is correct return True
	Desclaration of make_hint custom service
	Args:
			(MakeHp) req: the request of client composed by
			(string) arg: the type of hints that robot wants to acquire
	Returns:
			(string) hint: the instance of the argument requested 
	"""
	rospy.init_node('check_hypothesis')
	convalidate_service=rospy.Service('hp_convalidation',ConvalidateHp,clbk_convalidation)
	make_service=rospy.Service('make_hint',MakeHp,clbk_make_hint)
	print('Ready to convalidate a hypotesis')
	rospy.spin()
	
	
if __name__ == '__main__' :
	main()
