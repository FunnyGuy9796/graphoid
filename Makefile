all:
	g++ -o graphoid main.cpp interpreter/interpreter.cpp

clean:
	rm -f graphoid