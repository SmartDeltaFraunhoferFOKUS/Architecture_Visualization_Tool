import re
import tempfile
import subprocess
import os

# Input log file path
log_file_path = r"D:\Tools\AVT\dualstackLogs\new\evcc_output_dump.txt"
output_puml_path = "state_diagram_with_notes.puml"

class log2diagram():

    def __init__(self, logfile_path) -> None:        
        # Initialize lists and dictionaries to track states, transitions, and notes
        self.states = []
        self.transitions = []
        self.notes = {}
        self.current_state = None
        self.current_note = []
        self.previous_state = None
        self.first_state = None
        self.log_file = logfile_path
        
        

    def generate_puml(self):
        # get PlantUML statements from the state machine definition 
        puml_statements = []
        puml_statements.append("@startuml")
        puml_statements.append("skinparam state {\n  BackgroundColor LightBlue\n}")

        # Add initial state
        if self.first_state:
            puml_statements.append(f"[*] --> {self.first_state}")

        # Define states
        for state in self.states:
            puml_statements.append(f"state {state}")

        # Define transitions
        for from_state, to_state in self.transitions:
            puml_statements.append(f"{from_state} --> {to_state}")

        # Add notes for states
        for state, note in self.notes.items():
            puml_statements.append(f"note right of {state}\n{note}\nend note")

        # Add final state if the last state is "SessionStop"
        if self.previous_state == "SessionStop":
            puml_statements.append("SessionStop --> [*]")

        puml_statements.append("@enduml")

        # Return the full PlantUML content as a single string
        return "\n".join(puml_statements)
    
    def get_state_tranisition_info(self):
        # Regex patterns to match state entries, exits, and running states
        enter_pattern = r"\[enter\]: (\w+)"
        exit_pattern = r"\[exit\]: (\w+)"
        running_pattern = r"\[running\]: (\w+)"

        # Parse the log file
        with open(self.log_file, "r") as file:
            for line in file:
                line = line.strip()

                # Check for state entry
                enter_match = re.search(enter_pattern, line)
                if enter_match:
                    next_state = enter_match.group(1)

                    # Record the first state entered
                    if not self.first_state:
                        self.first_state = next_state

                    # If there's a previous state, link it to the current (next) state
                    if self.previous_state:
                        self.transitions.append((self.previous_state, next_state))

                    # If there's a current state, finalize its note
                    if self.current_state:
                        if self.current_note:
                            self.notes[self.current_state] = "\n".join(self.current_note)
                            self.current_note = []

                    # Update the current and previous states
                    self.previous_state = next_state
                    self.current_state = next_state
                    if next_state not in self.states:
                        self.states.append(next_state)

                    continue  # Skip this line as it's already processed

                # Check for state exit
                exit_match = re.search(exit_pattern, line)
                if exit_match:
                    exit_state = exit_match.group(1)
                    if exit_state == self.current_state:
                        # Finalize note for the current state
                        if self.current_note:
                            self.notes[self.current_state] = "\n".join(self.current_note)
                            self.current_note = []
                        # Update previous state to the exited state
                        self.previous_state = exit_state
                        self.current_state = None

                    continue  # Skip this line as it's already processed

                # Skip running state line
                if re.search(running_pattern, line):
                    continue

                # Capture any text as a note if we are inside a state
                if self.current_state:
                    if (line is not None and len(line)>0):
                        self.current_note.append(line)    
        
        return self.generate_puml()                
                              
    def generate_svg(self, puml_content, plantuml_jar_path):

        # Create a temporary file for the PlantUML content
        with tempfile.NamedTemporaryFile(delete=False, suffix=".puml") as temp_puml_file:
            temp_puml_file.write(puml_content.encode('utf-8'))
            temp_puml_file_path = temp_puml_file.name

        # Create a temporary file to store the SVG output
        svg_output_path = temp_puml_file_path.replace(".puml", ".svg")

        try:
            # Run PlantUML to generate SVG using the temp file
            subprocess.run(
                ["java", "-jar", plantuml_jar_path, "-tsvg", temp_puml_file_path],
                check=True
            )

            # Read the generated SVG file
            with open(svg_output_path, "r") as svg_file:
                svg_content = svg_file.read()

            return svg_content  # Return the SVG content as a string

        finally:
            print("done")
            # Clean up temporary files
            os.remove(temp_puml_file_path)
            if os.path.exists(svg_output_path):
                os.remove(svg_output_path)