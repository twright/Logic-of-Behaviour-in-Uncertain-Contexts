from flowstar.Interval cimport Interval
from flowstar.Monomial cimport Monomial

from libcpp.vector cimport vector
from libcpp.list cimport list as clist
from libcpp.string cimport string


# Minimal imports here to avoid circular cimport,
# main imports in TaylorModel.pxd
cdef extern from "TaylorModel.h" namespace "flowstar" nogil:
    cdef cppclass TaylorModel:
        pass

    cdef cppclass TaylorModelVec:
        pass


cdef extern from "Polynomial.h" namespace "flowstar" nogil:
    vector[Interval] factorial_rec
    vector[Interval] power_4
    vector[Interval] double_factorial


    cdef cppclass HornerForm:
        HornerForm()
        HornerForm(const Interval & I)

        void intEval(Interval & result, const vector[Interval] & domain) const

        void insert(TaylorModel & result, const TaylorModelVec & vars, const vector[Interval] & varsPolyRange, const vector[Interval] & domain, const Interval & cutoff_threshold) const
        void insert_ctrunc(TaylorModel & result, const TaylorModelVec & vars, const vector[Interval] & varsPolyRange, const vector[Interval] & domain, const int order, const Interval & cutoff_threshold) const


    cdef cppclass Polynomial:
        Polynomial()
        Polynomial(const Interval & constant, const int numVars)
        Polynomial(const vector[Interval] & coefficients)
        Polynomial(const Monomial & monomial)
        Polynomial(const clist[Monomial] & monos)
        Polynomial(const int varID, const int degree, const int numVars)
        Polynomial(const Polynomial & poly)

        void intEval(Interval & result, const vector[Interval] & domain) const
        Polynomial operator + (const Polynomial & polynomial) const
        Polynomial operator - (const Polynomial & polynomial) const
        Polynomial operator * (const Polynomial & polynomial) const
        Polynomial operator * (const Interval & I) const
        void LieDerivative(Polynomial & result,
                           const vector[Polynomial] & f) const

        Polynomial & operator = (const Polynomial & polynomial)
        # transform the polynomial into a Horner form
        void toHornerForm(HornerForm & result) const
        void mul_assign(const Interval & I)    # Polynomial & operator += (const Polynomial & polynomial)
        # Polynomial & operator -= (const Polynomial & polynomial)
        # Polynomial & operator *= (const Polynomial & polynomial)
        # Polynomial & operator *= (const Interval & I)
        void substitute(const vector[int] & varIDs, vector[Interval] & intVals)
        void derivative(Polynomial & result, const int varIndex) const
        void ctrunc(Interval & remainder, const vector[Interval] & domain, const int order)
        void insert(TaylorModel & result, TaylorModelVec & vars, const vector[Interval] & varsPolyRange, const vector[Interval] & domain, const Interval & cutoff_threshold) const

        void toString(string & result, const vector[string] & varNames) const
        # string & as_str()


# Subclass Polynomial to allow access to monomials
cdef extern from * nogil:
    '''
    class PolyWrap: public flowstar::Polynomial {
        /*
        PolyWrap(flowstar::Polynomial & P) {
            this->monomials = P.monomials;
        }
        */

        public:
            std::list<flowstar::Monomial> getMonomials() {
                return this->monomials;
            }
    };
    '''
    cdef cppclass PolyWrap:
        PolyWrap()
        clist[Monomial] & getMonomials()

ctypedef PolyWrap* PolyWrapPtr
ctypedef Polynomial* PolynomialPtr
