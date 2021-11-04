#!/usr/bin/env python

import rospy
from armor_msgs.srv import * 
from armor_msgs.msg import * 
import sys

##Global variable
path=None
path=rospy.get_param("/path_to_load")
path=str(path)

def load_ontology(command,primary_command_spec,secondary_command_spec,args):
	"""
	Function used to load the ontology on the armor server
	Instanciate a client of the armor server
	Args:
			command: is the command to pass at armor to load the ontology
			primary_command_spec: is the primary command to pass at armor to load the ontology
			secondary_command_spec: is the secondary command to pass at armor to load the ontology
			args: is an array of arguments to pass at armor to load the ontology
	Returns:
			res: the armor service response
	"""
	rospy.wait_for_service('armor_interface_srv')
	armor_client=rospy.ServiceProxy('armor_interface_srv', ArmorDirective)
	req=ArmorDirectiveReq()
	req.client_name='cluedo_fsm'
	req.reference_name='cluedo_ontology'
	req.command=command
	req.primary_command_spec = primary_command_spec
	req.secondary_command_spec=secondary_command_spec
	req.args=args
	res=armor_client(req)
	return res



def main():
	"""
	The body of the main function
	Initialize the node as armor_interface
	Pass all the arguments to the load_ontology function
	
	"""
	rospy.init_node('armor_interface')
	response=load_ontology('LOAD', 'FILE' , '' , [path,'http://www.emarolab.it/cluedo-ontology','true', 'PELLET', 'true'])
	##Check if the ontology is correctly loaded
	if(response.armor_response.success==False):
		print('Error: cannot load the ontology')
		sys.exit()
	elif(response.armor_response.success==True):
		print('The ontology is correctly loaded')
	rospy.spin()
	sys.exit()

if __name__ == '__main__' :
	main()
