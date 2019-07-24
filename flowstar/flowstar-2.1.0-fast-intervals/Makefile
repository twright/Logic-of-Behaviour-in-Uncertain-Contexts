CXX = g++
include makefile.local
LIBS = -lmpfr -lgmp -lgsl -lgslcblas -lm -lglpk
OFLAGS = -O3 -march=native -mtune=native
CFLAGS = -I . -I $(GMP_HOME) -g $(OFLAGS) -std=c++11 -fPIC -frounding-math
# --ffast-math
LINK_FLAGS = -g -L$(GMP_LIB_HOME)
OBJS = Interval.o Matrix.o Polynomial.o Monomial.o Constraints.o Geometry.o TaylorModel.o Continuous.o Hybrid.o

all: flowstar lib

flowstar: $(OBJS) lex.fyy.o modelParser.tab.o modelParser.o
	$(CXX) $(OFLAGS) -w $(LINK_FLAGS) -o $@ $^ $(LIBS)

lib: $(OBJS) lex.fyy.o modelParser.tab.o
	ar rcs libflowstar.a $^

%.o: %.cc
	$(CXX) $(OFLAGS) -c $(CFLAGS) -o $@ $<
%.o: %.cpp
	$(CXX) $(OFLAGS) -c $(CFLAGS) -o $@ $<
%.o: %.c
	$(CXX) $(OFLAGS) -c $(CFLAGS) -o $@ $<

modelParser.tab.c: modelParser.y
	bison -d -v modelParser.y
	# bison --debug --verbose -d -v modelParser.y

lex.fyy.c: modelLexer.l modelParser.tab.c
	flex -P fyy modelLexer.l
	# flex --debug modelLexer.l

clean:
	rm -f flowstar *.o libflowstar.a *~ lex.fyy.c modelParser.tab.c modelParser.tab.h modelParser.output lex.yy.c
