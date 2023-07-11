import base64
from IPython.display import Image, display
import matplotlib.pyplot as plt
import cv2 as cv
import urllib
from PIL import Image
import requests
import os 

_mermaid_diagram_type = "stateDiagram-v2 "
_mermaid_formatted_file = r"C:\Users\sab\Downloads\Vulnerablity\SmartDelta\Akka\samples\poc\mermaid_uml_states.mmd"

def genStateMachine(graph):    
    graphbytes = graph.encode("ascii")
    base64_bytes = base64.b64encode(graphbytes)
    base64_string = base64_bytes.decode("ascii")
    url = "https://mermaid.ink/img/" + base64_string
    page = requests.get(url)   
    f_name = 'img.png'
    with open(f_name, 'wb') as f:
        f.write(page.content)
    
    im = Image.open("img.png")
    im.show()

def createFormattedFile(content, mermaid_formatted_file):
    f = open(mermaid_formatted_file, "w")
    f.write(content)
    f.close()

def generate_mermaid_diagram(mermaid_diagram_type, mermaid_formatted_file, mermaid_statements=None):
    #sample_diagram = " [*]-->Def\n Def-->Def:ANY_KEY\n Def-->caps_locked:CAPS_LOCK\n caps_locked-->Def:CAPS_LOCK\n caps_locked-->caps_locked:ANY_KEY"
    draw_string= get_draw_string(mermaid_statements, mermaid_diagram_type) 
    print("writing to a mermaid file...")
    createFormattedFile(draw_string, mermaid_formatted_file)
    print(".mmd file writtent to: ", mermaid_formatted_file)
    return draw_string
    #genStateMachine(draw_string)

def get_draw_string(mermaid_statements, mermaid_diagram_type):
    draw_string = mermaid_diagram_type + "\n"
    for statement in mermaid_statements:
        draw_string= draw_string + statement + "\n"
    return(draw_string)

if __name__ == '__main__':
    generate_mermaid_diagram(_mermaid_diagram_type, _mermaid_formatted_file)