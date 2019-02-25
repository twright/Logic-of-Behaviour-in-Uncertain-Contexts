from flowstar.Interval cimport Interval
from flowstar.Polynomial cimport Polynomial
from flowstar.TaylorModel cimport TaylorModel, TaylorModelVec
from flowstar.includeh cimport NAME_SIZE

from libcpp.vector cimport vector
from libcpp.string cimport string
from libcpp.list cimport list as clist
from libcpp cimport bool as cbool
from libcpp.map cimport map as cmap

cdef extern from "Continuous.h" namespace "flowstar" nogil:
  cdef vector[string] domainVarNames

  cdef cppclass Flowpipe:
    Flowpipe()
    Flowpipe(const TaylorModelVec & tmvPre_input,
             const TaylorModelVec & tmv_input,
             const vector[Interval] & domain_input)
    Flowpipe(const vector[Interval] & box, const Interval & I)

    void intEval(vector[Interval] & result,
                 const Interval & cutoff_threshold) const

  cdef cppclass ContinuousSystem:
    ContinuousSystem()
    # ContinuousSystem(const iMatrix & A_input, const iMatrix & B_input, const iMatrix & ti_input, const iMatrix & tv_input, const vector[Flowpipe] & initialSets_input);
    # ContinuousSystem(const upMatrix & A_input, const upMatrix & B_input, const upMatrix & ti_input, const upMatrix & tv_input, const vector[Flowpipe] & initialSets_input);
    ContinuousSystem(const TaylorModelVec & ode_input,
                     const vector[Flowpipe] & initialSets_input)
    ContinuousSystem(const vector[string] & strOde_input,
                     const vector[Flowpipe] & initialSets_input)
    ContinuousSystem(const ContinuousSystem & system)

    ContinuousSystem & operator = (const ContinuousSystem & system)

    vector[Flowpipe] initialSets
    TaylorModelVec tmvOde

    cbool bAuto

  cdef cppclass ContinuousReachability:
    CountinuousReachability()

    int run()
    int numOfFlowpipes()
    void prepareForPlotting()
    void prepareForDumping()
    void plot_2D(const cbool bProjected)
    # void plot_2D_GNUPLOT(FILE *fp, const cbool bProjected) const
    cbool declareStateVar(const string & vName)
    int getIDForStateVar(const string & vName) const
    cbool declareTMVar(const string & vName)
    cbool declarePar(const string & pName, const Interval & range)
    cbool declareTIPar(const string & pName)
    cbool declareTVPar(const string & pName)

    # Variables
    # TODO: are all of these needed?
    ContinuousSystem system     # the continuous system
    double step                 # the step size used in the reachability analysis
    double time                 # the time horizon for the reachability analysis
    int precondition            # the preconditioning technique
    vector[int] outputAxes # the output axes
    int plotSetting             # the plot setting
    int plotFormat              # the plot format
    int numSections             # the number of sections in each dimension
    int orderType               # the order type
    cbool bAdaptiveSteps        # adaptive step size?
    cbool bAdaptiveOrders       # adaptive order?
    vector[Interval] estimation # the remainder estimation for varying time step
    double miniStep             # the minimum step size
    vector[int] orders          # the order(s)
    vector[int] maxOrders       # the maximum orders
    int globalMaxOrder          # the maximum order
    cbool bPrint                # print?
    cbool bSafetyChecking       # check safety?
    cbool bPlot                 # plot?
    cbool bDump                 # dump?
    int integrationScheme       # integration scheme?
    Interval cutoff_threshold   # threshold
    clist[Flowpipe] flowpipes
    clist[int] flowpipes_safety
    clist[TaylorModelVec] flowpipesCompo
    clist[vector[Interval]] domains
    clist[cbool] flowpipes_contracted
    int maxNumSteps
    int max_remainder_queue
    long num_of_flowpipes
    char outputFileName[NAME_SIZE]
    vector[string] stateVarNames
    cmap[string, int] stateVarTab
    cmap[string, int] tmVarTab
    vector[string] tmVarNames
    cmap[string, int] parTab
    vector[string] parNames
    vector[Interval] parRanges
    cmap[string, int] TI_Par_Tab
    vector[string] TI_Par_Names
    cmap[string, int] TV_Par_Tab
    vector[string] TV_Par_Names
