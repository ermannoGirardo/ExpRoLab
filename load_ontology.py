#!/usr/bin/env python

import rospy
from armor_msgs.srv import * 
from armor_msgs.msg import * 
import sys

#Global variables
path='/root/ros_ws/src/exproblab_assignment_1/cluedo_ontology.owl'

#function to load the ontology
def load_ontology(command,primary_command_spec,secondary_command_spec,args):
	global amor_client 
	rospy.wait_for_service('amor_interface_srv')
	armor_client=rospy.ServiceProxy('armor_interface_srv', ArmorDirective)
	req=ArmorDirective()
	req.client_name='my_cluedo_game'
	req.reference_name='cluedo_ontology'
	req.command=command
	req.primary_command_spec = primary_command_spec
	req.secondary_command_spec=secondary_command_spec
	req.args=args
	res=armor_client(req)
	return res

#main function
def main():
	rospy.init_node('amor_interface')
	armor_response=load_ontology('LOAD','FILE',' ', [path,'http://www.emarolab.it/cluedo-ontology','true', 'PELLET', 'true'])
	if(armor_response.success==False):
		prinf('Error: cannot load the ontology')
		sys.exit()
	rospy.spin()
	sis.stop()

if __name__ == '__main__' :
	main()
