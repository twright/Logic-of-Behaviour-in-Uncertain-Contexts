from functools import partial, reduce

from sage.all import *

from interval_utils import *

__all__ = ['search_zero', 'isolate_roots']


def isolate_roots(f, fprime, domain, nudge=0.001):
    dl, du = domain.endpoints()
    while dl < du:
        z = search_zero(f, fprime, RIF(dl, du))
        if z is None:
            break
        else:
            dl = z.upper('RNDU') + nudge
            yield z


def search_zero(f, fprime, t0, epsilon=0.00001, theta=0.01, abs_inf=0.0001):
    bound_found = False
    t = t0
    tl = t.lower('RNDD')

    if 0 not in RIF(f(tl)):
        while not bound_found:
            # print 't =', t.str(style='brackets')
            tbak = t
            tl = t.lower('RNDD')
            d = extdiv(-f(tl), fprime(t), t - tl)
            if d is None:
                # print "stopping since presumed converged"
                # print "t = {}, fprime(t) = {}".format(
                #     t.str(style='brackets'),
                #     RIF(fprime(t)).str(style='brackets'))
                return None
            t = (tl + d).intersection(t)
            bound_found = int_dist(tbak, t) <= epsilon
        # print "found lower bound!"
    # else:
        # print "0 on lower boundary!"

    tuu = t.upper('RNDU')
    tl = tu = t.lower('RNDD')
    while (not (((0 in RIF(f(RIF(tl,tu))) or 0 in RIF(f(tl)))
            and (RIF(f(tu)) > 0 or RIF(f(tu)) < 0)))
            and tu < tuu):
        print "tu = {}".format(tu)
        tu = min((1 + theta)*tu + abs_inf, tuu)

    t = RIF(tl,tu)

    if tu < tuu:
        bound_found = False
        while not bound_found:
            # print 't =', t.str(style='brackets')
            tbak = t
            tu = t.upper('RNDU')
            d = extdiv(f(tu), fprime(t), tu - t)
            if d is None:
                print "stopping since presumed converged"
                print "t = {}, fprime(t) = {}".format(
                    t.str(style='brackets'),
                    RIF(fprime(t)).str(style='brackets'))
                # This means the root was on the lower boundary!
                return t
                # break
                # return None
            t = (tu - d).intersection(t)
            bound_found = int_dist(tbak, t) <= epsilon
        # print "found upper bound!"
    # else:
        # print "0 on upper boundary!"

    return t

    #t = RIF(t.lower('RNDD'))
#     Delta = infinity
#     while True:
#         #d = RIF(fprime(t))
#         #if 0 in d:
#         #raise Exception("0 in d!")
#         tl = RIF(t.lower('RNDD'))
# #         inflated = tl.union(t.center()
# #                           + (1 + theta)*(t - t.center())
# #                           + RIF(-abs_inf, abs_inf))
#         d = extdiv(-RIF(f(tl)), RIF(fprime(t)), t - tl)
#         if d is not None:
#             t1 = tl + d
#             print "t  =", t.str(style='brackets')
#             print "t1 =", t1.str(style='brackets')
#             print t.lower('RNDU'), t1.lower('RNDD'), t1.upper('RNDU'), t.upper('RNDD')
#             if t.lower('RNDU') < t1.lower('RNDD') <= t1.upper('RNDU') < t.upper('RNDD'):
#                 t = t1
#                 break
#         else:
#             t1 = t
       # t1 = RIF(tl - f(tl)/d)

        #Deltabak = Delta
        #Delta = int_dist(t, t1)
        #print Deltabak, Delta
       # inflated = t1.center() + (1 + theta)*(t1 - t1.center()) + RIF(-abs_inf, abs_inf)
     #   print "ti =", inflated.str(style='brackets')
     #   t = t0.intersection(inflated) #tl.union(inflated)) #RIF(1,1+theta))
        #if Delta >= (1 - theta) * Deltabak:
        #    raise Exception('Did not converge!')
