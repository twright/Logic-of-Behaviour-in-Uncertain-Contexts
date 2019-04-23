cdef class FlowstarPlotMixin:
    pass
    # def plot(self, x, y, bytes filename, int plot_type=?):
    # def wplot(self, str x, str y, int plot_type=?, bytes filename=?):

cdef class SagePlotMixin:
    pass
    # def sage_plot(self, x, duration=None, double step=?):
    # def sage_parametric_plot(self, str x, str y, double step=?):
    # def sage_plot_manual(self, x, double step=?):
    # def sage_interval_plot(self, str x, str y, double step=?, **kwargs):


cdef class SageTubePlotMixin:
    pass
    # def sage_time_tube_plot(self, str x, double step=?, joins=?):
    # def sage_tube_plot(self, str x, str y, double step=?, bint arrows=?,
    #                    straight=?, tight=?, boundaries=?, joins=?, **kwargs):
