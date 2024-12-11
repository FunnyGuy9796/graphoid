import sys
import re

class Interpreter:
    def __init__(self):
        self.memory = {}
        self.pointer = 0
        self.graph = {}
        self.debug = False
    
    def replaceMemRef(self, match):
        innerContent = match.group(1)

        if not innerContent:
            return str(self.memory.get(self.pointer, 0))
        
        try:
            indexVal = int(innerContent)
            targetPtr = self.pointer + indexVal
            return str(self.memory.get(targetPtr, 0))
        except ValueError:
            return match.group(0)
    
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
            expression = operation[4:-1]

            try:
                if self.debug:
                    print(f"DEBUG: Before SET | {self.pointer}: {self.memory.get(self.pointer, None)}")
                
                if expression.startswith("{") and expression.endswith("}"):
                    processedExpression = re.sub(r'\{(.*?)\}', self.replaceMemRef, expression)

                    if self.debug:
                        print(f"DEBUG: Processed Expression: {processedExpression}")
                        
                    result = eval(processedExpression)
                    self.memory[self.pointer] = result

                    if self.debug:
                        print(f"DEBUG: After SET | {self.pointer}: {self.memory.get(self.pointer, None)}")

                elif re.match(r"^-?\d+$", expression):
                    self.memory[self.pointer] = int(expression)
                else:
                    if self.debug:
                        print(f"DEBUG: Evaluating SET operation for {self.pointer}: {expression}")

                    evalValue = eval(
                        re.sub(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\b",
                            lambda match: str(self.memory.get(match.group(1), 0)),
                            expression)
                    )

                    self.memory[self.pointer] = evalValue
                
                if self.debug:
                    print(f"DEBUG: After SET | {self.pointer}: {self.memory[self.pointer]}")
            except Exception as e:
                print(f"Error: Failed evaluating SET operation: {operation} | Error: {e}")

        elif operation.startswith("INCREMENT"):
            if self.debug:
                print(f"DEBUG: Before INCREMENT | Pointer: {self.pointer} | Value: {self.memory.get(self.pointer, None)}")

            self.memory[self.pointer] = self.memory.get(self.pointer, 0) + 1

            if self.debug:
                print(f"DEBUG: After INCREMENT | Pointer: {self.pointer} | Value: {self.memory.get(self.pointer, None)}")
        
        elif operation.startswith("DECREMENT"):
            if self.debug:
                print(f"DEBUG: Before DECREMENT | Pointer: {self.pointer} | Value: {self.memory.get(self.pointer, None)}")

            self.memory[self.pointer] = self.memory.get(self.pointer, 0) - 1

            if self.debug:
                print(f"DEBUG: After DECREMENT | Pointer: {self.pointer} | Value: {self.memory.get(self.pointer, None)}")

        elif operation.startswith("OUTPUT"):
            content = operation[7:-1].strip()

            if self.debug:
                print(f"DEBUG: OUTPUT content raw: {content}")

            if content.startswith('"') and content.endswith('"'):
                stringContent = content[1:-1]

                formattedContent = re.sub(r'\{(.*?)\}', self.replaceMemRef, stringContent)
                print(formattedContent)
            else:
                print(self.memory.get(self.pointer, 0))
        
        elif operation.startswith("CHECK"):
            result = True if self.memory[self.pointer] != 0 else False

            if self.debug:
                print(f"DEBUG: Evaluating CHECK operation: {result}")
            return result
        
        elif operation.startswith("SHIFT"):
            direction = operation[6:-1].strip()
            shiftCount = direction.count(">") if ">" in direction else direction.count("<")

            if self.debug:
                print(f"DEBUG: Before SHIFT | Pointer: {self.pointer}")

            if "<" in direction:
                self.pointer -= shiftCount
            elif ">" in direction:
                self.pointer += shiftCount
            
            if self.debug:
                print(f"DEBUG: After SHIFT | Pointer: {self.pointer}")

        else:
            print(f"{operation} is not recognized")

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
        
        print("")

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

    if interpreter.debug:
        interpreter.displayGraph()

    interpreter.run()

if __name__ == "__main__":
    main()