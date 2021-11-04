#!/bin/bash

gnome-terminal --tab --title="start_nodes_load_ontology" -- bash -c "roslaunch exproblab_assignment_1 start_load.launch"
gnome-terminal --tab --title="cluedo_fsm" -- bash -c "sleep 3; rosrun exproblab_assignment_1 cluedo_fsm.py "
