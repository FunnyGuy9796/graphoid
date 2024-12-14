#include <iostream>
#include <fstream>
#include <string>
#include <regex>
#include <vector>
#include <unordered_map>
#include <sstream>
#include <iomanip>
#include <algorithm>
#include "exprtk.hpp"

using namespace std;

struct Node {
    string name;
    string operation;
    vector<string> edges;
};

class Interpreter {
    private:
        bool debug;
        string filePath;
        string program;
        vector<Node> nodes;
        unordered_map<string, string> nodeMap;
        Node nextNode;
        double result = 0.0;

        typedef exprtk::symbol_table<double> symbol_table_t;
        typedef exprtk::expression<double> expression_t;
        typedef exprtk::parser<double> parser_t;

        symbol_table_t symbol_table;
        expression_t expression;
        parser_t parser;

        string trim(const string& str);
        vector<string> split(const string& str, char delimiter);
        Node parseNode(const string& block);
        vector<Node> tokenizeProgram();
        Node getNode(const string& name);
        string replaceVariables(const string& operation);
        bool isExpression(const string& operation);
        double calcExpression(const string& body);
        string convertAnswer(double answer);

        void execNode(Node node);
    
    public:
        Interpreter(string& filePath, bool isDebug) : filePath(filePath), debug(isDebug) {
            expression.register_symbol_table(symbol_table);
        }
        void readProgram();
        void runProgram();
};