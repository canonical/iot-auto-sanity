import sys
from sanity.agent import start_agent

def main():
    #handle the args
    args = sys.argv[1:]
    if len(args) < 1:
        print("please assign your plan as example:\nauto-sanity <your plan file name>")
        sys.exit()

    # pass the configure file to real auto-sanity module
    start_agent(args[0])
