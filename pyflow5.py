from flowstar.reachability import Reach, Poly, get_power_4, get_factorial_rec, get_double_factorial, get_precision, set_precision
varsc = [b'local_t', b't', b'x']
pt = Poly(1, 't', 0, varsc)
px = Poly(-1, 'x', 1, varsc)
print "t' = {}\nx' = {}".format(pt, px)
C = Reach(
    [b'local_t', b"t", b"x"],
    [Poly(varsc), pt, px],
    [(0,0), (5,5)],
    5,
    0.1,
    order=3,
)
print C.res, C.num_flowpipes
