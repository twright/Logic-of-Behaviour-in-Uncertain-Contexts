from flowstar.Interval cimport Interval
from libcpp.vector cimport vector
from libcpp.string cimport string
from libcpp cimport bool as cbool

cdef extern from "Monomial.h" namespace "flowstar" nogil:
    cdef cppclass Monomial:
        Monomial()
        Monomial(const Interval & I, const vector[int] & degs)
        Monomial(const Monomial & monomial)
        Monomial(const Interval & I, const int numVars)

        int degree() const
        int dimension() const

        void intEval(Interval & result, const vector[Interval] & domain) const

        # interval evaluation of the monomial, we assume that the domain is normalized to [0,s] x [-1,1]^(d-1)
        void intEvalNormal(Interval & result, const vector[Interval] & step_exp_table) const
        void inv(Monomial & result) const

        Monomial & operator = (const Monomial & monomial)
        #  Why does Cython not like += !
        # Monomial & operator += (const Monomial & monomial)
        # Monomial & operator *= (const Monomial & monomial)
        const Monomial operator + (const Monomial & monomial) const
        const Monomial operator * (const Monomial & monomial) const

        cbool isLinear(int & index) const

        # void dump_interval(FILE *fp, const vector[string] & varNames) const
        # void dump_constant(FILE *fp, const vector[string] & varNames) const

        void toString(string & result, const vector[string] & varNames) const
        cbool classInvariantOK() const

        cbool operator < (const Monomial & b) const
        cbool operator == (const Monomial & b) const

        cbool center()

        int cutoff(Monomial & monoRem, const Interval & cutoff_threshold)
        int cutoff(const Interval & cutoff_threshold)

        void substitute(const int varID, const Interval & intVal)
        void substitute(const vector[int] & varIDs, const vector[Interval] & intVals)

        cbool substitute_with_precond(const vector[cbool] & substitution);

        void substitute(Monomial & result, const int varID, const Interval & intVal) const
        void substitute(Monomial & result, const vector[int] & varIDs, const vector[Interval] & intVals) const

        void extend(const int num)

# Subclass Polynomial to allow access to monomials
cdef extern from * nogil:
    '''
    class MonoWrap: public flowstar::Monomial {
        public:
            flowstar::Interval getCoefficient() {
                return this->coefficient;
            }

            std::vector<int> getDegrees() {
                return this->degrees;
            }
    };
    '''
    cdef cppclass MonoWrap:
        MonoWrap()
        Interval getCoefficient()
        vector[int] getDegrees()

ctypedef MonoWrap* MonoWrapPtr
ctypedef Monomial* MonomialPtr