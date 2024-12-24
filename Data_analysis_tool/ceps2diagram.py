import argparse
from email import message
from math import fabs
import re
#from tkinter.tix import ACROSSTOP
#from unittest import TestResult
#import display_graph as dp
import os
#import dashboard.dashboard as dashboard
import intrepret_trace  as it
import settings
#import build_diagram_abs as build_diagram

delimeter = "\u25B6"

class ceps2diagram():

    def get_mermaid_statements(self, complete_trans):
        statements= []        
        #pattern = r"(?P<from_state>\w+)\-(?P<trigger>\w*)\-\u25B6(?P<to_state>\w+)"
        for transition in complete_trans:
            m = re.match(it.pattern, transition)
            #print(m.groupdict())
            #print(m.groups())
            state_from = m.group("from_state")
            if(state_from == "Initial"):
                state_from = "[*]"
            state_to = m.group("to_state")
            trigger = m.group("trigger")
            if(len(trigger)>0):
                mermaid_statement = state_from + "-->" + state_to + ":"+ trigger 
            else:
                mermaid_statement = state_from + "-->" + state_to
            statements.append(mermaid_statement)
        return statements

    def generate_text_file(self, source, destination):
        #GENERATE TEXT FILE FROM CEPS INPUT FILE HERE"
        cmd="ceps {0} --pr | sed -e 's/\x1b\[[0-9;]*m//g' | tee {1}"
        os.system(cmd.format(source, destination))
        print("Generated s-expressions from input...")
        #subprocess.Popen(["script.sh"], shell=True)
        #subprocess.call(["ceps", location, "--pr", text_file_location])
        #subprocess.call(["sed", "-e", 's/\x1b\[[0-9;]*m//g', text_file_location ])
        #return text_file_location

    def get_complete_transitions(self, all_transitions):   
        #get indiviudal transitions and create mermaid statements from them

        # This list should contain all complete transitions, in ceps, when the source is same, the transitions are not
        # shown shown i.e a->b . -> c means a transitions to b and also to c under certain events.
        # so this list will contain: [a->b, a->c]
        complete_transition=[]
        #all transitions have ALL transitions in the file as list. eg: [[a->b . ->c], [c->d]]
        for state_transitions in all_transitions:        
            state_from=[]
            state_to=[]
            #now iterate through transitions in each line of the file (each line can have multiple transitions)
            for transition  in state_transitions:
                transitioning_states = re.split("\s+", transition)
                if(len(transitioning_states)<2):
                    #the second state after "." is state after trigger and the source state is the first state.
                    state_to = transitioning_states[0]
                else:
                    state_from = (transitioning_states[0])            
                    state_to = (transitioning_states[1])            
                complete_transition.append(state_from + state_to)                
        return complete_transition
        

    def parse_file(self, text_loc):
        get_states_next = False
        get_transitions_next = False

        #transition = r"(?P<transition>\s*Transitions:\s*)"
        #state_names= r"(?P<state_names>\s*States:\s*)"

        states= []
        all_state_transitions= []
        #mermaid_statements= []

        with open(text_loc, encoding='utf-8') as fp:
            lines = fp.readlines()
            for line in lines:
                #once states are read, set the flag false
                if (get_states_next):
                    states.extend(i.strip() for i in line.split(","))
                    get_states_next = False
                #get states
                if(re.match(it.state_names, line, flags=re.IGNORECASE)):
                    get_states_next = True

                #if there is a new line, this means the transitions are not continued anymore
                if(re.match("\n", line)):
                    get_transitions_next = False

                if(get_transitions_next):
                    all_state_transitions.append([i.strip() for i in line.split(".")])
                    #get_transitions(line)            

                if(re.match(it.transition, line, flags=re.IGNORECASE)):
                    get_transitions_next = True 
        
        return all_state_transitions
        #print(mermaid_statements)
        #return mermaid_statements
        #print(states)
        #print(all_state_transitions)

    def get_statements(self, text_location):
        all_state_transitions = self.parse_file(text_location)
        complete_trans = self.get_complete_transitions(all_state_transitions)
        return(self.get_mermaid_statements(complete_trans))
        
