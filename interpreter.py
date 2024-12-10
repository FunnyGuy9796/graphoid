import sys
import re

class Interpreter:
    def __init__(self):
        self.memory = {}
        self.graph = {}
    
    def readFile(self, filename):
        try:
            with open(filename, 'r') as file:
                program = file.read()
            return program
        except FileNotFoundError:
            print(f"Error: File not found")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def parseProgram(self, program):
        lines = program.splitlines()

        for line in lines:
            line = line.strip()
            if not line:
                continue

            nodeMatch = re.match(r"<([^>]+)>", line)
            if not nodeMatch:
                continue

            nodeName = nodeMatch.group(1)
            self.graph[nodeName] = {"edges": [], "operation": None}

            edgeMatch = re.search(r"\[([^]]+)]", line)
            if edgeMatch:
                edges = edgeMatch.group(1).split("|")
                self.graph[nodeName]["edges"] = [edge.strip() for edge in edges]

            operationMatch = re.search(r"\{(.+)\}", line)
            if operationMatch:
                operation = operationMatch.group(1)
                self.graph[nodeName]["operation"] = operation
    
    def execOp(self, operation):
        if operation.startswith("SET"):
            parts = operation[4:-1].split(", ")
            cell = parts[0]
            value = int(parts[1])
            self.memory[cell] = value

        elif operation.startswith("INCREMENT"):
            cell = operation[10:-1].strip()
            self.memory[cell] = self.memory.get(cell, 0) + 1
        
        elif operation.startswith("DECREMENT"):
            cell = operation[10:-1].strip()
            self.memory[cell] = self.memory.get(cell, 0) - 1

        elif operation.startswith("OUTPUT"):
            content = operation[7:-1].strip()
            if content.startswith('"') and content.endswith('"'):
                stringContent = content[1:-1]
                formattedContent = re.sub(
                    r"\{([a-zA-Z0-9_]+)\}",
                    lambda match: str(self.memory.get(match.group(1), 0)),
                    stringContent
                )

                print(formattedContent)
            else:
                print(self.memory.get(content, 0))
        
        elif operation.startswith("COMPARE"):
            condition = operation[8:-1].strip()
            return eval(condition, {}, self.memory)

    def run(self):
        currNode = "start"
        while currNode != "end":
            nodeData = self.graph.get(currNode)
            if not nodeData:
                print(f"Error: Node '{currNode}' not found")
                break

            operation = nodeData["operation"]
            if operation:
                result = self.execOp(operation)
            
            edges = nodeData["edges"]
            if len(edges) == 1:
                currNode = edges[0]
            elif len(edges) == 2:
                currNode = edges[0] if result else edges[1]
            else:
                print(f"Error: Node '{currNode}' has invalid edges")
                break
    
    def displayGraph(self):
        print("Parsed Graph:")

        for node, details in self.graph.items():
            print(f"Node: {node}")
            print(f"    Edges: {details["edges"]}")
            print(f"    Operation: {details["operation"]}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python interpreter.py <filename>")
        return
    
    filename = sys.argv[1]
    interpreter = Interpreter()
    
    programContents = interpreter.readFile(filename)
    if not programContents:
        return
    
    interpreter.parseProgram(programContents)

    # interpreter.displayGraph()

    print("\nRunning Program:")
    interpreter.run()

if __name__ == "__main__":
    main()