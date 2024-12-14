#include "interpreter/interpreter.h"

int main(int argc, char* argv[]) {
    if (argc < 2) {
        cerr << "Error: No .grd file provided" << endl << "Usage: " << argv[0] << " <file_path>" << endl;
        return 1;
    }

    string filePath = argv[1];
    bool debugMode = false;

    if (argc >= 3 && string(argv[2]) == "--debug") {
        debugMode = true;
    }

    Interpreter interpreter(filePath, debugMode);

    try {
        interpreter.readProgram();
        interpreter.runProgram();
    } catch (const exception& e) {
        cerr << "Error: " << e.what() << endl;
        return 1;
    }

    return 0;
}