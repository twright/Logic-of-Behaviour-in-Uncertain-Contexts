from functools import partial
from sage.all import RIF, QQ
import sage.all as sg
from typing import Optional


__all__ = ('int_dist', 'finterval', 'intervals_approx_eq',
           'fintervals', 'int_sorted', 'inner_inverse_minkowski',
           'inner_shift_back', 'inner_minkowski', 'interval_subseteq',
           'function_max_width', 'containment_failures',
           'containment_failure_plots', 'check_containment', 'inflation_plot',
           'inflation_plot', 'plot_comparison', 'plot_full_comparison',
           'isub', 'extdiv')


def isub(a, b):
    al, au = a.endpoints()
    bl, bu = b.endpoints()
    if al <= bl <= au <= bu:
        return RIF(al, bl)
    elif bl <= al <= bu <= au:
        return RIF(bu, au)
    elif al in b and au in b:
        return None
    #elif a.overlaps(b):
    #    return a
    else:
        return a


def extdiv(a, b, d):
    a = RIF(a)
    # print 'b = {}'.format(repr(b))
    b = RIF(b)
    al, au = a.endpoints()
    bl, bu = b.endpoints()
    if 0 not in b:
        return (a/b).intersection(d) if (a/b).overlaps(d) else None
    elif al > 0:
        return isub(d, RIF(al/bl, al/bu))
    elif au < 0:
        return isub(d, RIF(au/bu, au/bl))
    else:
        return d


def inner_inverse_minkowski(I : RIF, J : RIF) -> Optional[RIF]:
    # I - J, smallest possible answer (underapproximate)
    il, iu = RIF(I).edges()
    jl, ju = RIF(J).edges()
    kl = il - ju
    ku = iu - jl
    if sg.infinity in I:
        return RIF(kl.upper('RNDU'), sg.infinity)
    elif kl.overlaps(ku):
        return None
    else:
        return RIF(kl.upper('RNDU'), ku.lower('RNDD'))


def inner_minkowski(I : RIF, J : RIF) -> Optional[RIF]:
    # I + J, smallest possible answer (overapproximate)
    il, iu = RIF(I).edges()
    jl, ju = RIF(J).edges()
    kl = (il + ju).lower('RNDD')
    ku = (iu + jl).upper('RNDU')
    return RIF(kl, ku) if kl <= ku else None


def inner_shift_back(K, J):
    if J not in RIF:
        J = RIF(J)
    tl, tu = J.edges()
    Ktl = inner_inverse_minkowski(K, tl)
    Ktu = inner_inverse_minkowski(K, tu)

    if Ktl is None or Ktu is None:
        return None
    elif Ktl.overlaps(Ktu):
        return Ktl.intersection(Ktu)
    else:
        return None


def finterval(I):
    if I is None:
        return repr(I)

    I = RIF(I)
    a, b = I.endpoints()
    try:
        ra, rb = a.floor(), b.ceil()
    except ValueError:
        ra = rb = None
    if (ra is not None
            and rb is not None
            and abs(ra - a) < 1e-9 and abs(rb - b) < 1e-9):
        return str(ra) if ra == rb else '[{} .. {}]'.format(ra, rb)
    else:
        # return f"[{QQ(I.lower())}..{QQ(I.upper())}]"
        return I.str(style='brackets')

def fqqinterval(I):
    if I is None:
        return repr(I)

    I = RIF(I)
    a, b = I.endpoints()
    try:
        ra, rb = a.floor(), b.ceil()
    except ValueError:
        ra = rb = None
    if (ra is not None
            and rb is not None
            and abs(ra - a) < 1e-9 and abs(rb - b) < 1e-9):
        return str(ra) if ra == rb else '[{} .. {}]'.format(ra, rb)
    else:
        return f"[{QQ(I.lower())} .. {QQ(I.upper())}]"
        # return I.str(style='brackets')

def intervals_approx_eq(xs, ys, epsilon=1e-3):
    xs = list(map(RIF, xs))
    ys = list(map(RIF, ys))
    print('xs = {}\nys = {}'.format(list(map(finterval, xs)),
                                    list(map(finterval, ys))))
    return (len(xs) == len(ys)
            and all(int_dist(x, y) <= epsilon for x, y in zip(xs, ys)))


def int_dist(I, J):
    il, iu = RIF(I).edges()
    jl, ju = RIF(J).edges()
    # Round up/down endpoints so as to overapproximate the real distance
    return max((il - jl).upper('RNDU'), (jl - il).upper('RNDU'),
               (iu - ju).upper('RNDU'), (ju - iu).upper('RNDU'))


def fintervals(space_domain):
    if space_domain is None:
        return repr(space_domain)
    return '[{}]'.format(', '.join(map(finterval, space_domain)))


def fqqintervals(space_domain):
    if space_domain is None:
        return repr(space_domain)
    return '[{}]'.format(', '.join(map(fqqinterval, space_domain)))


def int_sorted(kxs):
    kxs = map(partial(sorted, key=lambda x: (x[0], x[1].endpoints())), kxs)
    return sorted(kxs, key=lambda xs: [(k, x.endpoints()) for k, x in xs])


def interval_subseteq(x, y):
    xl, xu = RIF(x).endpoints()
    yl, yu = RIF(y).endpoints()
    return yl <= xl <= xu <= yu


def function_max_width(f, a, b, step):
    return max(
        max(xi.diameter() for xi in f(RIF(x, x + step)))
        for x in sg.srange(a, b, step)
    )


def containment_failures(proj, f, g, a, b, step):
    for x in sg.srange(a, b, step):
        val_f = proj(f(x)) # + RIF(0, step))
        val_g = proj(g(x)) # + RIF(0, step))
        if not interval_subseteq(val_f, val_g):
            yield x, val_f, val_g


def containment_failure_plots(proj, f, g, a, b, step):
    plt_f = sg.Graphics()
    plt_g = sg.Graphics()
    
    for x, val_f, val_g in containment_failures(proj, f, g, a, b, step):
        plt_f += sg.line([(x, val_f.lower() - 1), (x, val_f.upper() + 1)], color='red')
        plt_g += sg.line([(x, val_g.lower() - 1), (x, val_g.upper() + 1)], color='red')
        
    return plt_f, plt_g


def check_containment(f, g, a, b, step):
    for x in sg.srange(a, b, step):
        vals_f = f(x) # + RIF(0, step))
        vals_g = g(x) # + RIF(0, step))
        for (val_f, val_g) in zip(vals_f, vals_g):
            assert interval_subseteq(val_f, val_g),\
                f"{finterval(val_f)} should be a subset of {finterval(val_g)} at time {finterval(x)}"


def inflation_ratio(f, g, a, b, step):
    width_f = function_max_width(f, a, b, step)
    width_g = function_max_width(g, a, b, step)
    return width_g / width_f


def check_inflation(f, g, limit, a, b, step):
    assert inflation_ratio(f, g, a, b, step) <= limit,\
         f"Function inflation limit {limit} exceeded!"


def inflation_plot(g, ref, time_range, cutoff, yrange=None):
    return sg.region_plot(
        lambda t, _: g(t).diameter() > cutoff*ref,
        time_range,
        yrange=yrange,
        incol='pink',
        alpha=0.5,
    )


def plot_comparison(f, time_range, rch, solution, inits,
                    containment_check_step=None,
                    inflation_cutoff=None,
                    inflation_calc_step=None):
    def sol(t):
        return solution(*inits, t)
    
    def sol_min(t):
        return f(sol(t)).lower()
    
    def sol_max(t):
        return f(sol(t)).upper()
    
    def reach_min(t):
        return f(rch(t)).lower()
    
    def reach_max(t):
        return f(rch(t)).upper()
    
    if containment_check_step is not None:
        cont_f, cont_g = containment_failure_plots(
            f,
            sol,
            rch,
            *time_range,
            containment_check_step,
        )
    else:
        cont_f = sg.Graphics()
        cont_g = sg.Graphics()
    
    plt_f = sg.plot((sol_min, sol_max), time_range)
    plt_g = sg.plot((reach_min, reach_max), time_range)
    ymin = min([plt_f.ymin(), plt_g.ymin()])
    ymax = max([plt_f.ymax(), plt_g.ymax()])
        
    if inflation_cutoff is not None:
        ref = function_max_width(lambda t: [f(sol(t))],
                                *time_range, inflation_calc_step)
        yrange_g = f(rch(RIF(*time_range))).endpoints()
        infl = inflation_plot(lambda t: f(rch(t)), ref, time_range,
                                inflation_cutoff,
                                yrange=yrange_g)
    else:
        infl = sg.Graphics()
        
    combined_plot_f = plt_f + cont_f
    combined_plot_f.set_aspect_ratio(1/8)
    combined_plot_g = plt_g + cont_g + infl
    combined_plot_g.set_aspect_ratio(1/8)
    combined_plot_f.ymin(ymin)
    combined_plot_g.ymin(ymin)
    combined_plot_f.ymax(ymax)
    combined_plot_g.ymax(ymax)

    
    return sg.graphics_array(
        [combined_plot_f, combined_plot_g],
        ncols=1,
    )


def plot_full_comparison(time_range, rch, solution, inits,
                        containment_check_step=None,
                        inflation_cutoff=None,
                        inflation_calc_step=None):
    return sg.graphics_array(
        [plot_comparison(lambda v: RIF(v[0]), time_range, rch,
                         solution, inits,
                         containment_check_step=containment_check_step,
                         inflation_cutoff=inflation_cutoff,
                         inflation_calc_step=inflation_calc_step),
         plot_comparison(lambda v: RIF(v[1]), time_range, rch,
                         solution, inits,
                         containment_check_step=containment_check_step,
                         inflation_cutoff=inflation_cutoff,
                         inflation_calc_step=inflation_calc_step)],
        ncols=1,
    )