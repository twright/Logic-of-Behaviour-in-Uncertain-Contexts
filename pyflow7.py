from flowstar.reachability import Poly

varsd = [b't', b'x', b'y']
qt = Poly(1, 't', 0, varsd)
qx = Poly(-1, 'y', 1, varsd)
qy = Poly(1, 'x', 1, varsd)

print qy
print "2*x = {}".format(2*qy)
print "x*2 = {}".format(qy*2)

# print "t' = {}\nx' = {}\ny' = {}".format(qt, qx, qy)
# D = Reach(
#     varsd,
#     [qt, qx, qy],
#     [(0,0), (4,5), (1,2)],
#     5,
#     0.1,
#     order=3,
# )
# print "res =", D.res
# print "num flowpipes =", D.num_flowpipes
# D.plot(b'x', b'y', b'resd')
