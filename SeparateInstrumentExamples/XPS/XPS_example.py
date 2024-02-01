# -*- coding: utf-8 -*-
"""
Created on Sun Jan 28 18:47:48 2024

@author: osjac
"""

from time import sleep
import numpy as np

from PyQt5 import QtWidgets, uic
import sys
from newportxps import NewportXPS


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        #Load UI
        uic.loadUi('XPS_example_UI.ui', self)
        
        #Define some variables 
        self.commands = np.empty((0,4),dtype=np.float32) #as 4 axis of motion
        #This code is currently hard coded for 4 groups each with
        #a single stage, axis are X, Y, Z, theta
        self.commands_text = ""
        self.commands_names = []
        self.stage_names = []
        
        
        
        #==========Main Window============
        #Getting main page widgets
        self.statusLabel = self.findChild(QtWidgets.QLabel, "statusLabel")
        self.connectButton = self.findChild(QtWidgets.QPushButton, "connectButton")
        self.homeButton = self.findChild(QtWidgets.QPushButton, "homeButton")
        self.killButton = self.findChild(QtWidgets.QPushButton, "killButton")
        self.errorLabel = self.findChild(QtWidgets.QLabel, "errorLabel")
        self.addressLine = self.findChild(QtWidgets.QLineEdit, "addressLine")
        self.portLine = self.findChild(QtWidgets.QLineEdit, "portLine")
        
        #Set what functions buttons run
        self.connectButton.clicked.connect(self.connect)
        self.killButton.clicked.connect(self.kill)
        self.homeButton.clicked.connect(self.home)
        
        
        #==========Waypoint Tab============
        #get waypoint tab widgets
        self.waypoint1 = self.findChild(QtWidgets.QPushButton, "waypoint1Button")
        self.waypoint2 = self.findChild(QtWidgets.QPushButton, "waypoint2Button")
        self.waypoint3 = self.findChild(QtWidgets.QPushButton, "waypoint3Button")
        self.endButton = self.findChild(QtWidgets.QPushButton, "endButton")        
        self.runButton = self.findChild(QtWidgets.QPushButton, "runButton")
        self.clearButton = self.findChild(QtWidgets.QPushButton, "clearButton")
        self.commandBox = self.findChild(QtWidgets.QPlainTextEdit, "commandTextEdit")
        self.commandLabel = self.findChild(QtWidgets.QLabel, "commandLabel")
        self.action1_x = self.findChild(QtWidgets.QDoubleSpinBox, "action1_x")
        self.action1_y = self.findChild(QtWidgets.QDoubleSpinBox, "action1_y")
        self.action1_z = self.findChild(QtWidgets.QDoubleSpinBox, "action1_z")
        self.action1_theta = self.findChild(QtWidgets.QDoubleSpinBox, "action1_theta")
        self.action2_x = self.findChild(QtWidgets.QDoubleSpinBox, "action2_x")
        self.action2_y = self.findChild(QtWidgets.QDoubleSpinBox, "action2_y")
        self.action2_z = self.findChild(QtWidgets.QDoubleSpinBox, "action2_z")
        self.action2_theta = self.findChild(QtWidgets.QDoubleSpinBox, "action2_theta")
        self.action3_x = self.findChild(QtWidgets.QDoubleSpinBox, "action3_x")
        self.action3_y = self.findChild(QtWidgets.QDoubleSpinBox, "action3_y")
        self.action3_z = self.findChild(QtWidgets.QDoubleSpinBox, "action3_z")
        self.action3_theta = self.findChild(QtWidgets.QDoubleSpinBox, "action3_theta")
        self.progBar = self.findChild(QtWidgets.QProgressBar, "progressBar")
        
        #Set what functions buttons run
        self.waypoint1.clicked.connect(lambda: self.enterWaypoint(1))
        self.waypoint2.clicked.connect(lambda: self.enterWaypoint(2))
        self.waypoint3.clicked.connect(lambda: self.enterWaypoint(3))
        self.endButton.clicked.connect(lambda: self.enterWaypoint(None))
        self.clearButton.clicked.connect(self.waypointClear)
        self.runButton.clicked.connect(self.waypointRun)
        
        
        #==========Manual Tab============
        #get manual tab widgets
        self.moveButton = self.findChild(QtWidgets.QPushButton, "moveButton")
        self.group1_disp = self.findChild(QtWidgets.QSpinBox, "spinBox_g1_disp")
        self.group1_edit = self.findChild(QtWidgets.QSpinBox, "spinBox_g1_edit")
        self.group2_disp = self.findChild(QtWidgets.QSpinBox, "spinBox_g2_disp")
        self.group2_edit = self.findChild(QtWidgets.QSpinBox, "spinBox_g2_edit")
        self.group3_disp = self.findChild(QtWidgets.QSpinBox, "spinBox_g3_disp")
        self.group3_edit = self.findChild(QtWidgets.QSpinBox, "spinBox_g3_edit")
        self.group4_disp = self.findChild(QtWidgets.QSpinBox, "spinBox_g4_disp")
        self.group4_edit = self.findChild(QtWidgets.QSpinBox, "spinBox_g4_edit")
        
        #Set what functions buttons run
        self.moveButton.clicked.connect(self.manualMove)
        

        #Show the UI
        self.show()
        
        
        
    #currently unused
    def setErrorMsg(self, errorText):
        self.errorLabel.setText(errorText)
        #print("ERROR ENCOUNTERED: ", errorText)
    #currently unused    
    def setStatusMsg(self, statusText):
        self.statusLabel.setText(statusText)
    
    
    def waypointClear(self):
        '''
        This function removes all prevously entered commands for waypoint system
        and resets the progress bar.
        '''
        self.commandBox.clear()
        self.commandLabel.clear()
        self.commands_text = ""
        self.commands = np.empty((0,4),dtype=np.float32)
        self.commands_names = []
        self.progBar.setValue(0)
        
        
    def updateCommandBox(self):
        '''
        Updates the command box with the command string, the commandBox object is
        the main containor for the command string. As it can be editied in the UI.
        '''
        self.commandBox.setPlainText(str(self.commands_text))
        
        
    def enterWaypoint(self, wID):
        '''
        Adds a waypoint to the command string (self.command_text). Gets inputs 
        from spin boxes in the UI. If the string format is changed, the function 
        makeCommandList() must also be updated.
        
        Parameters
        ----------
        wID : Int
            This indicates what button has been pushed (defined in __init__).
        '''
        if wID == 1:
            self.commands_text = self.commands_text + "waypoint1|{} {} {} {}| > ".format(self.action1_x.value(), self.action1_y.value(), self.action1_z.value(), self.action1_theta.value())
        elif wID == 2:
            self.commands_text = self.commands_text + "waypoint2|{} {} {} {}| > ".format(self.action2_x.value(), self.action2_y.value(), self.action2_z.value(), self.action2_theta.value())
        elif wID == 3:
            self.commands_text = self.commands_text + "waypoint3|{} {} {} {}| > ".format(self.action3_x.value(), self.action3_y.value(), self.action3_z.value(), self.action3_theta.value())
        else:
            self.commands_text = self.commands_text + "end"
        self.updateCommandBox()#update the UI with the entered waypoint
    
    
    def makeCommandList(self):
        '''
        Contructs a 2d array to hold the waypoint commands. This is a numpy array
        with colunm num equal to the number of axis and row num the number of 
        waypoints. The commands produced are just 4dim coords, NOT how much to 
        move by.
        '''
        self.commands = np.empty((0,4),dtype=np.float32)
        command_split = self.commands_text.split(">")
        for command in command_split:
            #ignore ending parts or other splits
            if command == " " or command.strip() == "end":  
                continue
            #print("command: ",command)
            spliter = command.split("|")
            name, moveCom = spliter[0], spliter[1].split(" ")
            
            to_append = np.array(moveCom, dtype=np.float32)
            
            self.commands = np.vstack((self.commands,to_append))
            self.commands_names.append(name)
        #print(self.commands)
        
    
    def move2pos(self,command):
        '''
        Move to position defined in command.
        '''
        self.xps.move_group(group="Group1", pos = command[0])
        self.xps.move_group(group="Group2", pos = command[1])
        self.xps.move_group(group="Group3", pos = command[2])
        self.xps.move_group(group="Group4", pos = command[3])
        
        self.update_Pos()#update displaied position
    
    
    def waypointRun(self):
        '''
        When the run button on the waypoint tab is pressed the command list is 
        first created. Then the function loops through this and preforms each
        action. While also updating the UI with its status. 
        
        Todo:
            Error capture needs to be added!!
        '''
        self.makeCommandList()
        command_num = len(self.commands_names)
        #print("command_num",command_num)
        #Loop through each commmand
        for i in range(command_num):
            #print("Doing {}".format(self.commands_names[i]))
            #Update UI with status
            self.commandLabel.setText("Doing {}".format(self.commands_names[i]))
            #logic for progress bar
            self.progBar.setValue(int((100/command_num)*(i+1))) 
            self.statusLabel.setText("Waypoint mission")
            app.processEvents() #this gets the UI to update while looping
             
            self.move2pos(self.commands[i])
        
        self.statusLabel.setText("Waypoints completed")
        app.processEvents()

            

            
    def connect(self):
        '''
        Attempt to connect to XPS. Gets address and port from UI. Will display
        any errors on the UI.
        
        Todo:
            Capture error msg from command line and put in the advanced tab,
            this also needs to be made.
            Capture stage info and XPS status report and put in info tab, this
            also is on the Todo list.
        '''
        address = self.addressLine.text()
        porty = self.portLine.text()
        if (address == "") or (porty == ""):
            self.errorLabel.setText("Error: enter port and address")
            app.processEvents()  #this gets the UI to update while in if
            return
        
        self.statusLabel.setText("Attempting to connect")
        
        try:
            #Address must be str, Port must be int
            self.xps = NewportXPS(address, port=int(porty))
        except:
            self.statusLabel.setText("Failed to connect")
            self.errorLabel.setText("Error: port or address invalid")
            return
        
        
        #Get all stage names so they can be called later
        for sname, info in self.xps.stages.items():
            self.stage_names.append(sname)
        
        #print("Stage Names:",self.stage_names)
        
        #Update position reading on UI
        self.update_Pos()
        
        #Print status of XPS
        #print(self.xps.status_report())
        
        self.statusLabel.setText("Connected")


    def kill(self):
        '''
        Kills all groups. Currently hard coded for the XPS in Idris Lab. 
        
        Todo:
            Make the function use the XPS info to kill all stages. Use 
            self.stage_names to do this.
        '''
        self.xps.kill_group(group="Group1")
        self.xps.kill_group(group="Group2")
        self.xps.kill_group(group="Group3")
        self.xps.kill_group(group="Group4")
        self.statusLabel.setText("Killed all")


    def home(self):
        '''
        Initiazes and homes all groups. Will kill all first as a safegard.
        '''
        self.kill()
        self.statusLabel.setText("Initializing and Homing")
        app.processEvents()
        self.xps.initialize_allgroups()
        self.xps.home_allgroups()
        self.statusLabel.setText("Ready")


    def update_Pos(self):
        '''
        Updates the UI position reading with current positions.
        
        Todo:
            set all no matter the amount by looping through self.stage_names.
            May not be possible without making UI adjust to XPS connected on
            the fly.
        
        '''
        self.group1_disp.setValue(int(self.xps.get_stage_position(self.stage_names[0])))
        self.group2_disp.setValue(int(self.xps.get_stage_position(self.stage_names[1])))
        self.group3_disp.setValue(int(self.xps.get_stage_position(self.stage_names[2])))
        self.group4_disp.setValue(int(self.xps.get_stage_position(self.stage_names[3])))


    def manualMove(self):
        '''
        Moves the stage to position defined in the manual move tab. Currently 
        hard coded with group names.
        
        Todo:
            Possibly merge with self.move2pos()
        '''
        self.statusLabel.setText("Performing Manual Move")
        app.processEvents()
        where_to_move1 = self.group1_edit.value()
        where_to_move2 = self.group2_edit.value()
        where_to_move3 = self.group3_edit.value()
        where_to_move4 = self.group4_edit.value()
        self.xps.move_group(group="Group1", pos =where_to_move1)
        self.xps.move_group(group="Group2", pos =where_to_move2)
        self.xps.move_group(group="Group3", pos =where_to_move3)
        self.xps.move_group(group="Group4", pos =where_to_move4)
        
        #Update position reading on UI
        self.update_Pos()
        self.statusLabel.setText("Ready")


#This with run when python file is run.
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Ui() #Inisilize UI window object
    sys.exit(app.exec_()) #Kills app when closing UI 