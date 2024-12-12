import os
import sys
import re
from typing import Dict, Any

class Interpreter:
    def __init__(self, program: str):
        self.program = program
        self.nodes = {}
        self.currNode = 'START'
        self.variables = {}
        self.debug = False
    
    def replaceVar(self, match):
        key = match.group(0)[2:-1]
        node = self.nodes[key]

        return str(node['command'])
    
    def getVar(self, match):
        key = match.group(0)[1:-1]
        node = self.nodes[key]

        return node
    
    def parseProgram(self):
        pattern = r"\[(\w+)\s*\{([^}]*)\}\s*->\s*([\w\s|]*)\]"
        matches = re.findall(pattern, self.program, re.DOTALL)

        for name, command, transitions in matches:
            command = command.strip()
            transitions = [t.strip() for t in transitions.split('|')]
            self.nodes[name] = {
                'command': command,
                'transitions': transitions
            }
        
        if self.debug:
            print(f"\nParsed Graph:")

            for nodeName, node in self.nodes.items():
                print(f"{nodeName} | Command: {node['command']} | Transitions: {node['transitions']}")
    
    def parseCommand(self, command: str):
        newCommand = re.sub(r"\$\[.*?\]", self.replaceVar, command)

        if self.debug:
            print(f"Parsed Command: {newCommand}")
        
        return newCommand
    
    def execNode(self, nodeName: str):
        if nodeName not in self.nodes:
            raise ValueError(f"NODE ERROR: {nodeName} not found")
        
        node = self.nodes[nodeName]
        command = node['command']
        transitions = node['transitions']

        newCommand = self.parseCommand(command)

        if "print(" in newCommand:
            exec(newCommand)
        
        if "set(" in newCommand:
            setOp = newCommand.split(",")
            dest = setOp[0].strip().replace(setOp[0][:4], '', 1)
            value = setOp[1].strip()[:-1]

            if self.debug:
                print(f"set operation: {str(setOp)}")
            
            result = eval(value)
            destNode = self.nodes[dest]

            destNode['command'] = result
        
        if "if" in newCommand:
            condition = newCommand.split("if", 1)[1].strip()
            
            if self.debug:
                print(f"if statement: {condition}")
            
            try:
                return eval(condition)
            except Exception as e:
                raise ValueError(f"CONDITION ERROR: {condition} | {e}")

        if self.debug:
            print(f"Executing {nodeName}: {newCommand} | {transitions}")
    
    def run(self):
        transitions = self.nodes[self.currNode]

        while (self.currNode != "END"):
            result = self.execNode(self.currNode)
            current_node = self.nodes[self.currNode]
            transitions = current_node['transitions']

            if not transitions:
                break

            self.currNode = transitions[1] if result else transitions[0]

            if self.debug:
                print(f"Executing node {self.currNode} | Result: {result}")
        
        self.execNode("END")

def main():
    if len(sys.argv) < 2:
        print("Usage: python interpreter.py <filename>")
        return
    
    filePath = sys.argv[1]
    fileName, fileExtension = os.path.splitext(filePath)

    if fileExtension != '.grd':
        print(f"Supported file types: .grd | File: {fileName}.{fileExtension}")
        return

    with open(filePath, 'r') as file:
        fileContents = file.read()

    interpreter = Interpreter(fileContents)
    
    interpreter.parseProgram()
    interpreter.run()

if __name__ == "__main__":
    main()