states =  ["user1.Initial", 
"user1.ArriveFloorIN",
"user1.waiting",
"user1.elevator", 
"user1.elevator.Initial", 
"user1.elevator.callreceived",
"user1.elevator.decision",
"user1.elevator.decision.Initial",
"user1.elevator.goingup",
"user1.elevator.neutral",
"user1.getin",
"user1.elevator.goingdown", 
"user1.GoFloorOUT",
"user1.ExitSystem",
"user1.giveup",
"user1.final"]
trace_regex_message =  r'(?P<state_pattern>[a-zA-Z0-9_.]+[+-])'
state_from = r'(?P<state_from>[a-zA-Z0-9_.]+\-)'
state_to = r'(?P<state_to>[a-zA-Z0-9_.]+\+)'


