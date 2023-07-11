from math import fabs
from operator import truediv
import re
import intrepret_trace as it
import display_graph as dp
#import build_diagram_abs as build_diagram

class seq2diagram():

    def parse_file(self, text_loc):
        print("opening log file for processing...")    
        actors = []
        mermaid_statements_body = []
        with open(text_loc, encoding='utf-8') as fp:        
            lines = fp.readlines()        
            for i in range(0, len(lines)):
                print("Line:", i)
                '''Check if the line is properly formatted. 
                    Everything that does not satisfy the format is ignored and is not considered as a valid log line'''
                m = re.match(it.trace_pattern, lines[i]) # a line has a trigger i.e. a -trigger-> b
                message_source = []
                message_target = []                                
                if(m is not None):                    
                    match_dict = m.groupdict()
                    from_state = match_dict["from_state"]
                    to_state = match_dict ["to_state"]
                    trigger =  match_dict["trigger"]
                    print("line:{0}{1}{2}".format(from_state, to_state, trigger))

                    if(from_state is not None):
                        '''
                        from_state is of format:   a.b.s- ab.s2- 

                        here a is a super state machine and state machine b is a substate machine, while s is a state name
                        '''
                        for from_state_change in re.split("\s+", from_state):
                            if(len(from_state_change)>0): #if there is a space in the string, space is considered as one of the strings to parse. So skip the space
                                #only select state machines from the string and remove the state (so select [a,b])
                                individual_state_changes = from_state_change.split('.')
                                from_state_machines =  individual_state_changes[:-1] if len(individual_state_changes)>1 else individual_state_changes[0]
                                #get the current machine (so select [b])      
                                from_state_machine_current = from_state_machines[-1]
                                #add the state machine to "message source" list 
                                if from_state_machine_current not in message_source:
                                    message_source.append(from_state_machine_current)
                                #add the actor to the list 
                                if(from_state_machine_current not in actors):                              
                                    actors.append(from_state_machine_current)
                    else:
                        print("malformed source data. Message source format incorrect.")
                    if(to_state is not None):
                        '''
                        to_state is of format:    a.b.s+ ab.s2+ 

                        here a is a super state machine and state machine b is a substate machine, while s is a state name
                    
                        '''
                        for to_state_change in re.split("\s+", to_state):
                            if(len(to_state_change)>0):
                                #only select state machines from the string and remove the state (so select [a,b])         
                                individual_state_changes = to_state_change.split('.')               
                                to_state_machines =  individual_state_changes[:-1] if len(individual_state_changes)>1 else individual_state_changes[0]
                                #get the current machine (so select [b])
                                to_state_machine_current = to_state_machines[-1]
                                #add the state machine to "message source" list 
                                if to_state_machine_current[0] not in message_target:
                                    message_target.append(to_state_machine_current)

                                #add the actor to the list 
                                if(to_state_machine_current[0] not in actors):
                                    actors.append(to_state_machine_current)
                    else:
                        print("Malformed source data. Message target format incorrect.")
                    
                    diff_source_target_couple = [] #list of list of message source and the corresponding message target when both source and target are same actors (State Machines)
                    same_source_target_couple = [] #list of list of message source and the corresponding message target when both source and target are different actors (State Machines)
                    #if the source and target and diff, this will have more priority if source and source are same for a event. for example:
                    #in 
                    #a.s- -trigger->a.s1+ a.b.s3+
                    # then message source should be a and target should be b BUT in
                    # a.s- -trigger-> a.s1+
                    # source and target should be same (so self calls)
                     
                    print("message sources:", message_source) 
                    print("message targets:", message_target)
                    for message_source_machine in message_source:
                        for message_target_machine in message_target:
                            if(message_source_machine == message_target_machine):
                                same_source_target_couple.append([message_source_machine, message_target_machine])
                            else:
                                diff_source_target_couple.append([message_source_machine, message_target_machine])
                    
                    print("same source-targets:", same_source_target_couple)
                    print("different source-targets", diff_source_target_couple)

                    if(len(diff_source_target_couple)>0):
                        for source_target in diff_source_target_couple:
                            final_statement = source_target[0] + "->>" + source_target[1] + ":" + trigger 
                            mermaid_statements_body.append(final_statement)
                    elif len(same_source_target_couple)>0:
                        final_statement = same_source_target_couple[0][0] + "->>" + same_source_target_couple[0][1] + ":" + trigger 
                        mermaid_statements_body.append(final_statement)
                    print("...line end....")
                else:
                    #if there is no trigger, simply parse with white space and see if there are any state change expressions
                    print("no trigger:", lines[i])
                    expressions = re.split("\s+", lines[i])
                    for expression in expressions:                                                 
                         m = re.match(it.trace_pattern_state, expression) 
                         #if there is state change, then get the final (current state) i.e in a.s1- a.s2+, get a.s2
                         if (m is not None):                  
                           m_dict = m.groupdict()
                           state_pattern =  m_dict["state_pattern"]
                           if(len(state_pattern)>0 and state_pattern[-1] == '+'):
                                #get the state name and current state machine (actor) from a.b.s2+
                                all_machine = state_pattern.split(".")[0:-1]    # from a.b.s2+ get state machines as ["a", "b"]                         
                                current_actor = all_machine[-1] #from ["a", "b"] get b because it is current active machine
                                current_state = state_pattern.split(".")[-1] #get last item in a.b.s2+ as a state i,e s2
                                print(current_state)
                                #not need to display final or initial states
                                if (current_state.strip()[0:-1].lower() != "final" and current_state.strip()[0:-1].lower() != "initial"):
                                    statement =  "note over " + current_actor + ":" + current_state[0:-1] # get a as actor and s2 as note from a.s2+
                                    mermaid_statements_body.append(statement)
            #header_text= self.get_header_text(actors, logged_entity)
            #header_text  ="participant logged_entity as "+ logged_entity
            #mermaid_statements_header.append(header_text)
            complete_mermaid_statement = mermaid_statements_body        
            #final_statements = self.get_statements_with_loops(complete_mermaid_statement)
            print(complete_mermaid_statement)
            final_statements = self.handle_merged_logs(complete_mermaid_statement)
            return final_statements
        

    def handle_merged_logs(self, complete_mermaid_statements):
        #if the next statement has a complete diff actor then the current statement has caused triggering of another statemachine. 
        # Thus, the trigger should then result in calling of that statemachine 
        #    user1->>user1:CallUp
        #    note over user1:waiting
        #    note over elevator:neutral
        #    decision->>decision:AnyCalls
        # here, the very next state change after Callup is decision. So this Callup has resulted in calling the decision subroutine
        #    (although there is state change only on user1, but runtime should be differnt that just state chagne)
        final_statements = []
        for i in range(0, len(complete_mermaid_statements)): #there is no need to read the last line
            current_statement = complete_mermaid_statements[i]            
            m1 = re.match(it.trace_pattern_mermaid, current_statement)
            if(m1 is not None):                
                match_dict_source = m1.groupdict()
                current_source_actor = match_dict_source["actor_1"]
                current_dest_actor = match_dict_source ["actor_2"]
                current_trigger =  match_dict_source["trigger"]
                #get the next mermaid statement that contains actors with state change
                m2 = None
                j=i+1
                while m2 is None:   
                    if (j>= len(complete_mermaid_statements)):
                        break                 
                    next_statement = complete_mermaid_statements[j]
                    m2 =  re.match(it.trace_pattern_mermaid, next_statement)
                    j= j+1
                if m2 is not None:
                    match_dict_next = m2.groupdict()
                    next_source_actor = match_dict_next["actor_1"]
                    #next_dest_actor = match_dict_next ["actor_2"]
                    #next_trigger =  match_dict_next["trigger"]                       
                    if(next_source_actor == current_source_actor):
                        final_statements.append(current_source_actor + "->>" + current_dest_actor + ":" + current_trigger)
                    elif(next_source_actor != current_source_actor):
                        final_statements.append(current_source_actor + "->>" + next_source_actor + ":" + current_trigger)  
                else:
                    final_statements.append(complete_mermaid_statements[i])          
            else:
                final_statements.append(complete_mermaid_statements[i])
        return final_statements