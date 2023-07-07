import re
from collections import OrderedDict
""""
Enter here the list of regex representing message types in traces or output from ceps intrepreter (S-expressions).
"""

#log specific regex. 
#log body in actor.state -trigger-> actor.state2 format
trace_pattern = r'(?P<from_state>([a-zA-Z0-9_.]+[+-]\s*)+)\s*\-(?P<trigger>\w+)\-\u25B6\s*(?P<to_state>([a-zA-Z0-9_.]+[+-]\s*)+)'
#matched state chagne formats like a.state+  or a.state-
trace_pattern_state = r'(?P<state_pattern>[a-zA-Z0-9_.]+[+-])'
#expectation of the next message
trace_pattern_mermaid = r'(?P<actor_1>\w+)->>(?P<actor_2>\w+)\:(?P<trigger>\w+)'

#regex matches for heatmaps
state_to =r'(?P<state_to>[a-zA-Z0-9_.]+\+)'
state_from =r'(?P<state_from>[a-zA-Z0-9_.]+\-)'

#ceps state machine specific regex
#ceps intrepreter returns what the grammar thinks of given syntax. This returns Transitions and States
transition = r"(?P<transition>\s*Transitions:\s*)"
state_names= r"(?P<state_names>\s*States:\s*)"
#pattern used to represent individual state transition
pattern = r"(?P<from_state>\w+)\-(?P<trigger>\w*)\-\u25B6(?P<to_state>\w+)"