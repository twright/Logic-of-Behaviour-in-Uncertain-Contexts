from __future__ import absolute_import, division, print_function

from libc.string cimport strcpy
from subprocess import call

from flowstar.Polynomial cimport Polynomial
from flowstar.Continuous cimport ContinuousReachability
from flowstar.reachability cimport CReach
from flowstar.poly cimport Poly
from flowstar.poly import index_fn
from flowstar.Interval cimport Interval


cdef class FlowstarPlotMixin:
    def plot(CReach self, x, y, bytes filename, plot_type=1):
        if not self.ran:
            raise Exception('Not ran!')

        cdef CReach cself = <CReach?>self
        cdef ContinuousReachability * C = &cself.c_reach

        C.plotFormat = 0 # GNUPLOT format
        C.plotSetting = plot_type
        cdef char * c_filename = filename
        if len(filename) >= 100:
            raise Exception('Filename too long!')
        strcpy(C.outputFileName, c_filename)

        # prepare for plotting -- must be done here, not in run since this
        # depends on the output axes
        self.prepare()
        # set bProjected = True since apparently prepareForPlotting has
        # already projected the flowpipes to the correct dimensions

        C.outputAxes.clear()
        C.outputAxes.push_back(C.getIDForStateVar(x))
        C.outputAxes.push_back(C.getIDForStateVar(y))

        with self.global_manager:  # Use class's version of flowstar global variables
            # We set projected to False since we use prepareForDumping
            # which does not project the flowpipes to the output
            # dimensions for us
            C.plot_2D(False)

        # note: filename is unsanitized
        call(['gnuplot', './outputs/{}.plt'.format(filename)])

    def wplot(self, str x, str y, int plot_type=1, bytes filename = None):
        from wand.image import Image
        import uuid

        if filename is None:
            filename = bytes(uuid.uuid4())
        self.plot(x, y, filename, plot_type)
        img = Image(filename='./images/{}.eps'.format(filename), format='eps')
        img.rotate(90)
        return img

cdef class SagePlotMixin:
    def sage_plot(self, poly, duration=None, double step=1e-2, **kwargs):
        from sage.all import plot

        # If passed a variable name as an argument, look it up from
        # the field's generators
        if isinstance(poly, str):
            poly = Poly({str(g): g for g in self.R.gens()}[poly])
        else:
            poly = Poly(poly)

        if duration is None:
            duration = (0, float((<CReach?>self).c_reach.time))

        # Cache the evaluations
        ress = dict()

        def f(t):
            if t not in ress:
                ress[t] = (<CReach?>self).eval_poly(poly, (t - step, t + step))
            return ress[t]
        def fl(t):
            return f(t).lower()
        def fu(t):
            return f(t).upper()

        return plot([fl, fu],
                    duration,
                    plot_points=self.time//step,
                    **kwargs)

    def sage_parametric_plot(self, str x, str y, double step=1e-2):
        from sage.all import parametric_plot, RIF
        from functools import partial

        cdef int var_id_x = (<CReach?>self).c_reach.getIDForStateVar(x)
        cdef int var_id_y = (<CReach?>self).c_reach.getIDForStateVar(y)

        def f(t):
            return self((t, t+step))[var_id_x].center()
        def g(t):
            return self((t, t+step))[var_id_y].center()

        return parametric_plot((f, g), (0, float(self.c_reach.time)))

    def sage_plot_manual(self, x, double step=1e-1):
        from sage.all import Graphics, line

        p = Graphics()
        cdef int var_id = (<CReach?>self).c_reach.getIDForStateVar(x)
        res1 = self((-1e-7,1e-7))[var_id]
        lo1, hi1 = res1.lower(), res1.upper()
        cdef double t = 0

        for i in range(int(self.time/step)):
            t = step*i
            res = self((t, t+step))
            try:
                (lo, hi) = res[var_id].endpoints()
            except:
                print("warning: eval failed for t in [{}, {}]".format(t, t+step))
            p += line([(t, lo), (t+step, lo)])
            p += line([(t, lo1), (t, lo)])
            p += line([(t, hi), (t+step, hi)], color='#3bcc00')
            p += line([(t, hi1), (t, hi)], color='#3bcc00')
            lo1 = lo
            hi1 = hi

        return p

    def sage_interval_plot(self, str x, str y, double step=1e-1, poly = None, **kwargs):
        from sage.all import Graphics, polygon

        p = Graphics()
        cdef int var_id_x = (<CReach?>self).c_reach.getIDForStateVar(x)
        cdef int var_id_y = (<CReach?>self).c_reach.getIDForStateVar(y)
        cdef double t = 0
        # cdef Interval pres

        for i in range(int(self.time/step)):
            t = step*i
            res = self((t, t+step))
            try:
                (xlo, xhi) = res[var_id_x].endpoints()
                (ylo, yhi) = res[var_id_y].endpoints()
            except:
                print("warning: eval failed for t in [{}, {}]".format(t, t+step))

            # Choose colour based on p
            # col = 'default'
            col = kwargs.get('color', None)
            if poly is not None:
                pres = self.eval_poly(Poly(poly), (t, t+step)) #index_fn(poly)(res)
                if pres.lower() > 0:
                    col = 'green'
                if pres.upper() < 0:
                    col = 'red'

            p += polygon([(xlo, ylo), (xlo, yhi), (xhi, yhi), (xhi, ylo)],
                         fill=False,
                         **(kwargs if col is None
                                   else dict(color=col, **kwargs)))

        return p


cdef class SageTubePlotMixin:
    def sage_time_tube_plot(self, str x, double step=1e-1,joins=True):
        return self.sage_tube_plot('t', x, step, straight=True, joins=joins)

    def sage_tube_plot(self, str x, str y, double step=1e-1, bint arrows=False, straight=False, tight=False, boundaries=True, joins=True, **kwargs):
        from sage.all import line, Graphics, RIF, sqrt, arctan, tan, cos, sin, arrow, point, pi, vector

        p = Graphics()
        var_id_x = (<CReach?>self).c_reach.getIDForStateVar(x)
        var_id_y = (<CReach?>self).c_reach.getIDForStateVar(y)
        cx0 = cy0 = None
        cx = cy = None
        tx = ty = None
        rx = ry = None
        dx = dy = None
        r00 = r0 = r = None

        n = int(self.time//step)
        for i in range(n + 1):
            t = step*i
            if i < n:
                res = self((t, t+step))
            try:
                Ix = RIF(res[var_id_x])
                Iy = RIF(res[var_id_y])
            except:
                print("warning: eval failed for t in [{}, {}]".format(t, t+step))
            cx00, cy00 = cx0, cy0
            cx0, cy0 = cx, cy
            tx0, ty0 = tx, ty
            if i < n:
                cx, cy = Ix.center(), Iy.center()
                if cx0 is not None:
                    dx0, dy0 = dx, dy
                    dx, dy = (cx - cx0), (cy - cy0)
                    theta = pi/2 - arctan(dy/dx)

            r000 = r00
            r00 = r0
            r0 = r
            rx0, ry0 = rx, ry
            rx, ry = Ix.absolute_diameter()/2, Iy.absolute_diameter()/2
            r = sqrt(rx**2 + ry**2)

            if rx0 is None:
                pass
            elif straight:
                tx = 0
                ty = ry0
            elif tight:
                # This finds where we hit the bounding box -- does not work
                # well due to the edges interseTruecting
                if abs(tan(theta)) < 100 and (rx0 < ry0 or abs(tan(theta)) < 0.01):
                    print("A:", rx0, ry0, float(tan(theta)))
                    tx = rx0
                    ty = tx*tan(theta)
                else:
                    print("B:", rx0, ry0, float(tan(theta)))
                    ty = ry0
                    tx = ty*tan(theta)
            else:
                tx = r0 * cos(theta)
                ty = r0 * sin(theta)
            # if theta > pi/2:
            #     tx = -tx
            #     ty = -ty
            # if rx0 < ry0:
            #     tx = rx0
            #     ty = tx*tan(theta)
            # else:
            #     ty = ry0
            #     tx = ty/tan(theta)

            if cx00 is not None:
                # Draw width
                if joins:
                    p += line([(cx00 - tx0, cy00 + ty0),
                               (cx00 + tx0, cy00 - ty0)], linestyle='--',
                               **kwargs)

                # Connect subsequent lines (draw lines between their endpoints
                # chosing the pairs of endpoints which make the most
                # parallel lines)
                if boundaries:
                    if ( vector([tx0-tx, ty-ty0])*vector([tx-tx0, ty0-ty])
                       > vector([tx0 + tx, -ty-ty0])*vector([-tx-tx0, ty+ty0])):
                        p += line([(cx00 - tx0, cy00 + ty0),
                                   (cx0 - tx, cy0 + ty)], **kwargs)
                        p += line([(cx00 + tx0, cy00 - ty0),
                                   (cx0 + tx, cy0 - ty)], **kwargs)
                    else:
                        p += line([(cx00 - tx0, cy00 + ty0),
                                   (cx0 + tx, cy0 - ty)], **kwargs)
                        p += line([(cx00 + tx0, cy00 - ty0),
                                   (cx0 - tx, cy0 + ty)], **kwargs)

                # Draw arrows in the plotting direction
                if arrows:
                    p += point((cx00, cy00), size=100, **kwargs)
                    p += arrow((cx00, cy00),
                               (cx00 + 2*dx0/3, cy00 + 2*dy0/3),
                               **kwargs)

        if joins:
            p += line([(cx0 - tx, cy0 + ty),
                       (cx0 + tx, cy0 - ty)], linestyle='--', **kwargs)

        return p
