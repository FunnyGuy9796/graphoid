#include "interpreter.h"

string Interpreter::trim(const string& str) {
    auto start = str.find_first_not_of(" \t\n\r");
    if (start == string::npos) return "";

    auto end = str.find_last_not_of(" \t\n\r");
    return str.substr(start, end - start + 1);
}

vector<string> Interpreter::split(const string& str, char delimiter) {
    vector<string> tokens;
    stringstream ss(str);
    string token;

    while (getline(ss, token, delimiter)) {
        tokens.push_back(trim(token));
    }

    return tokens;
}

Node Interpreter::parseNode(const string& block) {
    Node node;

    auto nameStart = block.find('[') + 1;
    auto nameEnd = block.find('{', nameStart) - 1;
    node.name = block.substr(nameStart, nameEnd - nameStart);

    if (node.name == "NONE" || node.name.empty())
        throw runtime_error("Syntax Error: Invalid node name");

    auto opStart = block.find('{') + 1;
    auto opEnd = block.find('}', opStart);
    node.operation = trim(block.substr(opStart, opEnd - opStart));

    if (node.operation.empty())
        throw runtime_error("Syntax Error: Invalid node operation");

    auto edgeStart = block.find("->", opEnd);
    if (edgeStart != string::npos) {
        auto edgeStr = block.substr(edgeStart + 2);

        if (edgeStr.empty())
            throw runtime_error("Syntax Error: Invalid node edge(s)");

        node.edges = split(edgeStr, '|');

        for (auto& edge : node.edges) {
            if (!edge.empty() && edge.back() == ']') {
                edge.pop_back();
            }
        }
    }

    return node;
}

vector<Node> Interpreter::tokenizeProgram() {
    vector<Node> nodes;
    size_t pos = 0;
    size_t next;

    while ((next = program.find('[', pos)) != string::npos) {
        int bracketCount = 1;
        size_t blockEnd = next + 1;

        while (bracketCount > 0 && blockEnd < program.length()) {
            if (program[blockEnd] == '[') bracketCount++;
            if (program[blockEnd] == ']') bracketCount--;
            
            blockEnd++;
        }

        if (bracketCount != 0) {
            throw runtime_error("Syntax Error: Mismatched brackets");
        }

        string block = program.substr(next, blockEnd - next);
        nodes.push_back(parseNode(block));

        pos = blockEnd;
    }

    return nodes;
}

Node Interpreter::getNode(const string& name) {
    for (const auto& node : nodes) {
        if (node.name == name)
            return node;
    }

    throw runtime_error("Node not found: " + name);
}

void Interpreter::setNext(int result) {
    if (debug)
        cout << "Old nextNode: " << nextNode.name << " Old callNode: " << callNode.name << endl;

    if (result != 2) {
        if (!nextNode.edges.empty()) {
            if (nextNode.edges[result] != "NONE")
                nextNode = getNode(nextNode.edges[result]);
            else if (callNode.name != "NONE" && inFunction) {
                nextNode = getNode(callNode.edges[0]);
                
                inFunction = false;
                callNode.name = "NONE";
                callNode.operation = "";
                callNode.edges = {};
            }
        } else if (nextNode.name != "END")
            throw runtime_error("Runtime Error: Missing next node for execution");
    } else {
        inFunction = true;
        callNode = nextNode;
        nextNode = funcNode;
    }
    
    if (debug)
        cout << "nextNode: " << nextNode.name << " callNode: " << callNode.name << endl;
}

string Interpreter::replaceVariables(const string& operation) {
    stack<string> stack;
    string result;
    string temp;
    bool innerVar = false;

    for (size_t i = 0; i < operation.length(); i++) {
        if (operation[i] == '$' && i + 1 < operation.length() && operation[i + 1] == '[') {
            if (innerVar) {
                stack.push(temp);
                temp.clear();
            }

            innerVar = true;
            i++;
        } else if (operation[i] == ']' && innerVar) {
            string varName = temp;
            Node varNode = getNode(varName);
            temp.clear();
            innerVar = false;
            string varValue = varNode.operation;

            if (stack.empty())
                result += varValue;
            else {
                temp = stack.top();
                stack.pop();
                temp += varValue;
                innerVar = true;
            }
        } else {
            if (innerVar)
                temp += operation[i];
            else
                result += operation[i];
        }
    }

    if (innerVar) {
        result += "$[" + temp;
    }

    return result;
}

bool Interpreter::isExpression(const string& operation) {
    regex expressionRegex(R"(^[\d+\-*/()<>=!.\s]+$)");
    return regex_match(operation, expressionRegex);
}

double Interpreter::calcExpression(const string& body) {
    if (isExpression(body)) {
        if (!parser.compile(body, expression))
            throw runtime_error("Runtime Error: Unable to compute expression " + body);

        result = expression.value();

        if (debug)
            cout << "Expression: " << body << " Result: " << result << endl;
        
        return result;
    }

    return 0.0;
}

string Interpreter::convertAnswer(double answer) {
    string expResult;
    stringstream ss;

    ss << defaultfloat << setprecision(4) << answer;
    expResult = ss.str();

    if (expResult.empty())
        expResult = '0';
    else if (!expResult.empty() && expResult.back() == '.')
        expResult.pop_back();
    
    if (debug)
        cout << "Original Answer: " << answer << " String Answer: " << expResult << endl;

    return expResult;
}

void Interpreter::execNode(Node currNode) {
    string operation = replaceVariables(currNode.operation);
    string command = operation.substr(0, operation.find('('));
    string body;
    size_t openParen = operation.find('(');
    size_t closeParen = operation.find_last_of(')');

    if (openParen != string::npos && closeParen != string::npos && openParen < closeParen)
        body = operation.substr(openParen + 1, closeParen - openParen - 1);
    else
        throw runtime_error("Syntax Error: Missing '(' or ')': " + body);
    
    if (debug)
        cout << "Name: " << currNode.name << " Command: " << command << " Body: " << body << " Edge: " << currNode.edges[0] << endl;

    if (command == "print" && !body.empty()) {
        if (body.front() == '"')
            body.erase(0, 1);
        if (body.back() == '"')
            body.pop_back();
        
        cout << body << endl;

        setNext(0);
    } else if (command == "set" && !body.empty()) {
        vector<string> bodyParts = split(body, ',');

        if (bodyParts.size() != 2)
            throw runtime_error("Runtime Error: Invalid values for set() operation");
        
        double expResult = calcExpression(bodyParts[1]);
        string finalResult = convertAnswer(expResult);

        auto destNodeItr = find_if(nodes.begin(), nodes.end(), [&](const Node& n) {
            return n.name == bodyParts[0];
        });

        if (destNodeItr != nodes.end()) {
            destNodeItr->operation = finalResult;

            if (debug)
                cout << "Destination Node: " << destNodeItr->name << " New Value: " << destNodeItr->operation << endl;
        } else
            throw runtime_error("Runtime Error: Destination node not found for set() operation");
        
        setNext(0);
    } else if (command == "if" && !body.empty()) {
        result = calcExpression(body);

        setNext(static_cast<int>(result));
    } else if (command == "call" && !body.empty()) {
        funcNode = getNode(body);

        setNext(2);
    }
}

void Interpreter::readProgram() {
    ifstream file(filePath);

    if (!file.is_open()) {
        throw runtime_error("File Error: Could not open program file");
    }

    ostringstream buffer;
    buffer << file.rdbuf();

    program = buffer.str();

    file.close();
}

void Interpreter::runProgram() {
    try {
        nodes = tokenizeProgram();
        if (nodes.empty())
            throw runtime_error("Error: No nodes found in the program");

        for (const auto& node : nodes) {
            nodeMap[node.name] = node.operation;
        }

        if (debug) {
            cout << "Program Graph:" << endl;

            for (const auto& node : nodes) {
                cout << "Node: " << node.name << "\n";
                cout << "Operation: " << node.operation << "\n";
                cout << "Edges: ";
                
                for (const auto& edge : node.edges) {
                    cout << edge << " ";
                }

                cout << "\n\n";
            }
        }

        nextNode = getNode("START");
        
        while (true) {
            execNode(nextNode);

            if (nextNode.edges.size() < 1 || nextNode.name == "END")
                break;
        }

        nextNode = getNode("END");
        execNode(nextNode);

    } catch (const exception& e) {
        throw runtime_error("Error: " + string(e.what()));
    }
}