#!/usr/bin/env python

"""
.. module:: cluedo_fsm
   :platform: Unix
   :synopsis: Implementation of a FSM for playing cluedo game
.. moduleauthor:: Ermanno Girardo  <s4506472@studenti.unige.it>
Client to: <BR>
     /armor_interface_srv:  the armor server to manage ontologies
     
     /hp_convalidation: custom service to tell the hypothesis to the oracle
     
     /make_hint: custom service to acquire hints once the robot is in a room
     
     /time_to_move: custom service to generate the time to move to another room
     
     
     This node is the implementation of the state machine.
     It is composed by three states:
		-Moving: The robot starting from the Cluedo Room has to move to another room
						in order to acquire hints.
						This state simulate the motion of the robot, asking to simulation_time server 
						to compute the time needed to move from a room to another room.
		-Acquire Hints: Once the robot is arrived into the room, starts to acquire hints.
									There is a call to the oracle to making a hint. Via a custom service
									the oracle randomically chooses an instance of type specified by the client
									and return a string of the instace to the client.
									If the hypotesis is completed and not consistent then go to the next state 
									on the contrary if it is not return to moving state and  the Robot should 
									build a new hypotesis.
		-Tell Hypotesis: Once an hypotesis is completed and consistent the robot should go to the
									Cluedo Room and tell the hypotesis to the oracle. The oracle check each field 
									of the hypotesis and then says to the robot if the hypothesis is correct or not.
									Internally the oracle says for each of the three fields if it is correct or not.
									In this way, for example, if the robot knows that Mrs Peacock is the killer next 
									time that acquire hints avoids to acquire new hints for the killer.
									This is a chooice, in order to do not grow exponencially the number of hypothesis
									before knowing the solution.
  
"""
import roslib
import rospy
import smach
import smach_ros
import time
import random
import sys
from armor_msgs.srv import * 
from armor_msgs.msg import * 
from exproblab_assignment_1.srv import *


##Global Variables

##Define the armor server
armor_client=None
req = ArmorDirectiveReq()
req.client_name = 'cluedo_fsm'
req.reference_name = 'cluedo_ontology'

##time to detect hints in seconds
time_to_detect=3

##boolean values for the hints
true_who=False
true_where=False
true_what=False

##hypothesis counter
HP_counter=0

##path to save the onrology
path=None
path=rospy.get_param("/path_to_save")
path=str(path)

##variables to compute time to change room
##Suppose the robot starts in the cluedo room
from_room='Cluedo_Room'
to_room=None

##boolean for completed hypothesis
completed_hp=False

##varialable to generate a inconsistent hypotesis
inconsistent_count=1
inconsistent_list=''

def cut_string(string):
	"""
	Simple function to cut the armor response string
	Args:
			string:string to cut
	Returns:
			string:string cutted
	"""
	start=string.rfind('#')
	end=len(string)-1
	string=string[(start+1) : end]
	return string



# define state exploration
class Motion(smach.State):
	"""
	Motion state of FSM
	Args:
			smach.State: instance of a smach state
	"""
	def __init__(self):
		"""
		 initialisation function of the state Motion, it should not wait
		 Outcomes:
							enter_room: room that the robot should reach to acquire hints
		"""
		smach.State.__init__(self, 
								outcomes=['enter_room'])
        
	def execute(self, userdata):
		"""
		Body of the Motion State
		Args:
				self
				userdata: userdata
		"""
		global armor_client,from_room,to_room,time_to_explore,req
		##choose randomly next room  
		req.command = 'QUERY'
		req.primary_command_spec = 'IND'
		req.secondary_command_spec = 'CLASS' 
		req.args = ['PLACE']
		##res is the list of all PLACES into the ontology
		res = armor_client(req).armor_response.queried_objects
		##choose randomly an instance in the list
		room = random.choice(res)
		room=cut_string(room) 
		##if the room is Cluedo Room
		##choice another room
		while(room=='Cluedo_Room'):
			print('Cannot go to Cluedo Room to search hints')
			req.command = 'QUERY'
			req.primary_command_spec = 'IND'
			req.secondary_command_spec = 'CLASS' 
			req.args = ['PLACE']
			res = armor_client(req).armor_response.queried_objects
			room = random.choice(res)
			room=cut_string(room) 
		##Go to room
		to_room=room
		print('From : ' + str(from_room) + '  Move to:  ' + str(to_room))
		##Call the custom service to compute the time
		time_response=time_to_explore(str(from_room),str(to_room)).time
		#Exploration
		rospy.loginfo('Exploring')
		time.sleep(time_response)
		print('I am arrived in: ' + str(to_room))
		##update prev_room
		from_room=to_room
		return 'enter_room'
        
        
    
    
    
# define state make hypotesis
class Acquire_Hints(smach.State):
	def __init__(self):
		"""
		Initialization of Acquire_Hints state
		Args:
				outcomes:
								enter_cluedo_room: once an hypotesis is completed and consistent
								inconsistent_hypotesis: when an hypothesis is inconsistent go to Motion state
								incompleted_hypothesis:when an hypothesis is incompleted go to Motion state
				input_keys:
								killer: the acquired  murder 
								killer_weapon: the acquired killer weapon
								killer_place: the acquired killer place
				output_keys:
								killer: the acquired  murder 
								killer_weapon: the acquired killer weapon
								killer_place: the acquired killer place
		"""
		# initialisation function, it should not wait
		smach.State.__init__(self, 
								outcomes=['enter_cluedo_room','inconsistent_hypothesis','incompleted_hypothesis'],
								input_keys=['killer','killer_weapon','killer_place'],
								output_keys=['killer','killer_weapon','killer_place'])
        
	def execute(self, userdata):
		"""
		Body of the Acquire_Hints state
		"""
		global armor_client,make_hint_client,HP_counter,completed_hp
		print('Search for hints\n')
		##simulate time for searching a hint
		time.sleep(time_to_detect)
		##if is not correct the who hint QUERY a new WHO
		global true_who,true_where,true_what,inconsistent_count,inconsistent_list
		if(true_who==False):
			killer=make_hint_client('who').hint
			killer=cut_string(killer)
			userdata.killer=killer
			print('Detect a hint: the killer is: ' + str (userdata.killer))
		##if is not correct the where hint QUERY a new PLACE
		if(true_where==False):
			killer_place=make_hint_client('where').hint
			killer_place=cut_string(killer_place)
			##hint could not be cluedo room
			while(killer_place=='Cluedo_Room'):
				killer_place=make_hint_client('where').hint
				killer_place=cut_string(killer_place)
			userdata.killer_place=killer_place
			print('Detect a hint: the place is: ' + str (userdata.killer_place))
		##if is not correct the what hint QUERY a new WHO
		if(true_what==False):
			killer_weapon=make_hint_client('what').hint
			killer_weapon=cut_string(killer_weapon)
			userdata.killer_weapon=killer_weapon	
			print('Detect a hint: the weapon is: ' + str (userdata.killer_weapon))
		##ADD hypotesis
		hypothesis='HP'+str(HP_counter)
		HP_counter=HP_counter+1
		req.command = 'ADD'
		req.primary_command_spec = 'IND'
		req.secondary_command_spec = 'CLASS' 
		req.args = [hypothesis,'HYPOTHESIS']
		res = armor_client(req).armor_response.success
		if(res==False):
			print('Error to add the hypotesis\n')
		##ADD instances to the hypotesis
		req.command = 'ADD'
		req.primary_command_spec = 'OBJECTPROP'
		req.secondary_command_spec = 'IND'
		req.args = ['who',hypothesis,userdata.killer]
		res=armor_client(req).armor_response.success
		if(res==False):
			print('Error to add the killer to: ' + str(hypothesis))
		req.args = ['what',hypothesis,userdata.killer_weapon]
		res = armor_client(req).armor_response.success
		if(res==False):
			print('Error to add the weapon to: ' + str(hypothesis))
		req.args = ['where',hypothesis,userdata.killer_place]
		res = armor_client(req).armor_response.success
		if(res==False):
			print('Error to add the place to: ' + str(hypothesis))
		##Every 3 completed hypotesis generate the inconsistent hypotesis
		##And if the killer is not known yet
		if((inconsistent_count % 3 == 0)and(true_who==False)):
			killer=make_hint_client('who').hint
			killer=cut_string(killer)
			userdata.killer=killer
			print('Detect a hint: the killer is: ' + str (userdata.killer))
			##Add the instance to the hypotesis
			req.command = 'ADD'
			req.primary_command_spec = 'OBJECTPROP'
			req.secondary_command_spec = 'IND'
			req.args = ['who',hypothesis,userdata.killer]
			res=armor_client(req).armor_response.success
			if(res==False):
				print('Error to add the killer to: ' + str(hypothesis))	
		##UPDATE the ontology
		req.command = 'REASON'
		req.primary_command_spec = ''
		req.secondary_command_spec = ''
		req.args = ['']
		res = armor_client(req).armor_response.success
		if(res==False):
			print('Error: cannot update the ontology')
		##Check if the current hypotesis is completed
		req.command = 'QUERY'
		req.primary_command_spec = 'IND'
		req.secondary_command_spec = 'CLASS'
		req.args = ['COMPLETED']
		res = armor_client(req).armor_response.queried_objects
		i=0
		for x in res:
			x=cut_string(x)
			res[i]=x
			i=i+1
			if x==hypothesis:
				completed_hp=True
		##now res is an array of 'clean' strings
		print('The list of all completed hypothesis is: ' + str(res))
		##Check if the current hypothesis is not inconsistent
		##If this is Completed
		if(completed_hp==True):
			req.command = 'QUERY'
			req.primary_command_spec = 'IND'
			req.secondary_command_spec = 'CLASS'
			req.args = ['INCONSISTENT']
			res = armor_client(req).armor_response.queried_objects
			j=0
			for x in res:
				x=cut_string(x)
				res[j]=x
				j=j+1
				##if the instruction is true, the hp is inconsistent
				if x==hypothesis:
					inconsistent_count=inconsistent_count+1
					inconsistent_list=str(inconsistent_list) + str(x) + ',' 
					print('List of inconsistent hypothesis: ' + str(inconsistent_list))
					return 'inconsistent_hypothesis'
			inconsistent_count=inconsistent_count+1
			print('List of inconsistent hypothesis: ' + str(inconsistent_list))
			return 'enter_cluedo_room'
		else:
			##This case is not possible but is for future implementation
			return 'incompleted_hypothesis'


class Tell_Hypothesis(smach.State):
	def __init__(self):
		"""
		Initialization of the Tell_Hypothesis state
		Args:
				outcomes:
								incorrect_hypothesis: when an hyopothesis is evaulated incorrect go to Motion state
								correct_hypothesis:when an hypothesis is evaulated correct go to CASE_SOLVED
				input_keys:
								killer: the acquired  murder 
								killer_weapon: the acquired killer weapon
								killer_place: the acquired killer place
		"""
		smach.State.__init__(self,
								outcomes=['incorrect_hypothesis','correct_hypothesis'],
								input_keys=['killer','killer_weapon','killer_place'])
    
	def execute(self, userdata):
		"""
		Body of the Tell_Hypothesis state
		"""
		global true_what,true_where,true_who,armor_client,check_hp_client
		global make_hint_client,to_room
		to_room='Cluedo_Room'
		#Simulate time to arrive into cluedo_room
		time_response=time_to_explore(str(from_room),str(to_room)).time
		#print(time_response)
		print('Going to the cluedo room')
		##simulate time to enter into the cluedo room
		time.sleep(time_response)
		print('I am arrived in Cluedo Room')
		hp_to_check=ConvalidateHpRequest()
		hp_to_check.who=userdata.killer
		hp_to_check.where=userdata.killer_place
		hp_to_check.what=userdata.killer_weapon
		oracle_res=check_hp_client(hp_to_check)
		##check the value
		if(oracle_res.who==True):
			true_who=True
		if(oracle_res.where==True):
			true_where=True
		if(oracle_res.what==True):
			true_what=True
		##Check that all the three hints are true
		if((true_what==True)and(true_where==True)and(true_who==True)):
			print('The game is end')
			print('The killer is: ' +  str(hp_to_check.who))
			print('The place is: ' + str(hp_to_check.where))
			print('The weapon is:' + str(hp_to_check.what))
			##Save the Ontology
			req.command = 'SAVE'
			req.primary_command_spec = ''
			req.secondary_command_spec = ''
			req.args = [path]
			res = armor_client(req).armor_response.success
			if(res==False):
				print('Error:cannot save the ontology solution')
			return 'correct_hypothesis'
		else:
			print('The hypotesis is wrong')			
			return 'incorrect_hypothesis'
		return 


def main():
	"""
	Body of the main function
	Initialize the node as cluedo_FSM
	Create a client of the armor server to deal with armor
	Create a client of the hp_convalidation server to says the hypothesis to the oracle
	Create a client of the make_hint server to acquire hints
	Create a client of the time_to_move server to calculate the time needed to change room
	Create the SMACH state machine and define the outcomes of FSM as CASE_SOLVED
	"""
	global armor_client,check_hp_client,time_to_explore,make_hint_client
	rospy.init_node('cluedo_FSM')
	##Create services client
	armor_client = rospy.ServiceProxy('armor_interface_srv', ArmorDirective) 
	check_hp_client=rospy.ServiceProxy('hp_convalidation',ConvalidateHp)
	make_hint_client=rospy.ServiceProxy('make_hint',MakeHp)
	time_to_explore=rospy.ServiceProxy('time_to_move',TimeToWait)
	
	##Create a SMACH state machine
	sm = smach.StateMachine(outcomes=['CASE_SOLVED'])
	sm.userdata.killer = ' '
	sm.userdata.killer_weapon = ' '
	sm.userdata.killer_place = ' '
	##Open the container
	with sm:
		"""
		Function used to define the links between FSM' s states
		"""
		##Add states to the container
		smach.StateMachine.add('MOTION', Motion(), 
								transitions={'enter_room':'ACQUIRE_HINTS'})

		smach.StateMachine.add('ACQUIRE_HINTS', Acquire_Hints(), 
								transitions={'enter_cluedo_room':'TELL_HYPOTHESIS',
												'inconsistent_hypothesis':'MOTION',
												'incompleted_hypothesis':'MOTION'})

		smach.StateMachine.add('TELL_HYPOTHESIS', Tell_Hypothesis(), 
								transitions={'incorrect_hypothesis':'MOTION', 
											'correct_hypothesis':'CASE_SOLVED'})
                                            
	##Create and start the introspection server for visualization
	sis = smach_ros.IntrospectionServer('server_name', sm, '/SM_ROOT')
	sis.start()

	##Execute the state machine
	outcome = sm.execute()

	##Wait for ctrl-c to stop the application
	rospy.spin()
	sis.stop()


if __name__ == '__main__':
	main()                         





