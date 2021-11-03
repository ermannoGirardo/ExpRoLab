# First Assignment of the Experimental Robotics Lab course (Robotics Engineering / JEMARO, Unige) Ermanno Girardo S4506472

# Requirements:
Using the armor server deal with an ontology in order to play table game Cluedo.
The student has to develop a FSM in order to:
  * simulate the motion of the robot in the environment
  * once the robot is arrived to the room chosen, acquire hints
  * once the robot has acquired a completed and consistent hypothesis the robot should go to the Cluedo Room in order to says the hypothesis to the oracle
  * if the hypothesis is incorrect the robot should go to another room and acquire new hints

# Something more about Cluedo Game
Cluedo is a strategy table game playable from 2 to 6 players.
In order to play there are two entities in our context: The robot that navigating in the map should acquire hints via QR code scanner, and the oracle an omniscient entity that knows the correct hypothesis.
Following you can see a picture of the Cluedo Map.


![Cluedo_Map](https://user-images.githubusercontent.com/48509825/140074337-635a67c4-e5ed-4340-9403-d902389efe2e.jpg)


How the hints works?
In cluedo the player have to collect three types of hint: who is the murder, what is the weapon used to kill and where the murder was commmitted.
Once a player have a completed hypotesis (one instance for each type) can go to the Cluedo Room and he says the hypothesis his has in mind.
In the following image you can see the possibles hints for Cluedo game:


![Cluedo Hints](https://user-images.githubusercontent.com/48509825/140075102-e088b78b-9d2d-4dbd-bd1d-6f3cf8ce750f.jpg)


# The architecture of the project
The following is a component diagram of the architecture of the project that is useful to clarify the idea.

![CluedoArchitecture](https://user-images.githubusercontent.com/48509825/140076637-6e1165c7-56ed-4710-b3fd-2af7de0a5079.jpg)

# What you can find in this repository
## Scripts:
  * cluedo_fsm.py --> This is the FSM that simulate the cluedo game. It is developed as three states:
    1) Motion:  The robot starting from the Cluedo Room has to move to another room in order to acquire hints.
			 This state simulate the motion of the robot, asking to simulation_time custom server to compute the time needed to move from a room to another room.
    2) Acquire Hints: Once the robot is arrived into the room, starts to acquire hints.
			 There is a call to the oracle to making a hint. Via a custom service the oracle randomically chooses an instance of type specified by the client
			 and return a string of the instace to the client. If the hypotesis is completed and not consistent then go to the next state 
			 on the contrary if it is not return to moving state and  the Robot should build a new hypotesis.
    3) Tell Hypothesis: Once an hypotesis is completed and consistent the robot should go to the Cluedo Room and tell the hypotesis to the oracle. 
       The oracle check each field of the hypotesis and then says to the robot if the hypothesis is correct or not.
       Internally the oracle says for each of the three fields if it is correct or not. In this way, for example, if the robot knows that Mrs Peacock is the killer next 
			 time that acquire hints avoids to acquire new hints for the killer. This is a chooice, in order to do not grow exponencially the number of hypothesis 
       before knowing the solution.
       Another projectual choice is the fact that the robot for the most of the time acquires completed hypothesis. In order to show that the algorithm works also with 
       inconsistent hypothesis one every three hypothesis is inconsistent. Of course if the hypothesis is inconsistent the robot could not go to Cluedo Room but has to 
       go to another room and search new hints.
  * the_oracle.py --> Is the oracle node. He has to achieve two important task, developed via two custom services:
    1) Make randomic hints when the robot is arrived into a room. This is done via a custom service make_hint, a client is declared into the cluedo_fsm node
       that simply does a call to the service, passing a string of the type of hints the robot wants. The service response with an hint of the type specified.
       In order to make a hint the oracle make a query to the armor server.
    2) Once the robot has a complete and consistent hypothesis, it goes to the Cluedo Room and though a custom service, hp_convalidation, the robot is able to ask for
       each type of hints if is correct or not.
  * load_ontology.py --> this node has the purpose of loading the ontology into the armor server, passing an ontology already delevoped with all the hints possibles
                         in the figure above.  In order to do this all the armor parameters  must be setted properly.
  * simulation_time.py --> This node has the purpose of compute the euclidian distance between the robot where the robot is and the room that the robot wants to move.
                          Then assuming an average velocity of 1 m/s , the time is simply evaluated. Via a custom service time_to_momve is possible to pass two strings
                          "from_room" and "to_roomm" and the servervice return a float32 that is the time computed. This is possible through a dictionary of the rooms 
                          as in the figure of Cluedo's map above.
## Documentation:
You can find all the sphinx documentation into the docs folder.
In particular you can find more details about the source code.

## Launch:
* There is a launch file into the launch folder: start_load.launch
  This launch file execute all the nodes described above except for cluedo_fsm.py.
  Is not possible to put all into the same launch file because before execute cluedo_fsm a few seconds are passing.
  This file load all the ros parameter needed to play Cluedo, in particular:
    1) who: string referred to the name of the killer
    2) what: string referred to the name of killer's weapon
    3) where: string regerred to the name of killer's room
    4) path_to_load: is the absolute path referred to where the system should take 
* There is also a second launch file, load_start_game.sh, wich uses gnome terminals to execute all the nodes in a correct way.
## Ontology
You can find a cluedo_ontology.owl file wich contains all the instance of persons,places and weapons for cluedo table game as in the figure above.

# How to start the Simulation:
!!!Note!!! that this package works for sure for ROS noetic, for other ROS version is not already tested.
First you have to clone the package into your ros workspace/src:
```
git clone https://github.com/ermannoGirardo/exproblab_assignment_1
```
Now you have to build the solution into your ros_ws:
```
catkin_make --only-pkg-with-deps exproblab_assignment_1
```

Now you have to properly change the parameter, in particular the absolute path for load and save the ontology.
If you want to change the instances of the correct hypothesis, you can do it, but be sure that the names are identical to the instances into the .owl file.

* The first solution to start everything is the following:
  ```
  roslaunch exproblab_assignment_1 start_load.launch
  ```
  And after this you can execute the cluedo_fsm into another terminal:
  ```
  rosrun exproblab_assignment_1 cluedo_fsm.py
  ```
* For the second solution I create load_start_game.sh which uses gnome terminals.
  In this way is possible the automatical execution of cluedo_fsm.py after few seconds the execution of the launch file.
  So, first you have to install gnome terminal, if you haven't yet:
  ```
  apt install gnome-terminal
  ```
  Then you have to modify the permit of the file, in order to make it an executable file:
  ```
  chmode +x load_start_game.sh
  ```
  And now you can execute the file:
  ```
  ./load_start_game
  ```









