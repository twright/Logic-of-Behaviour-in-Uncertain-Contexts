from flowstar.reachability import Reach, Poly

vars = {'t': 0, 'x': 1}
t = Poly(1, 't', 1, vars)
x = Poly(1, 'x', 1, vars)
pt = Poly(1, 't', 0, vars)
px = Poly(-1, 'x', 1, vars)
print "t' = {}\nx' = {}".format(pt, px)

print("creating ContinuousReachability wrapper")
C = Reach(
    [b"t", b"x"],
    [pt, px],
    [(0,0), (5,5)],
    5,
    0.5,
    orders=[1, 2],
)

print("running...")
res = C.run()

stat = "ran successfully!" if 1 <= res <= 3 else "failed!"
print "{} -- {} flowpipes computed".format(stat, C.num_flowpipes)

print("plotting...")
C.wplot(dict, 't', 'x', b'res1')

varsd = {b't': 0, b'x': 1, b'y': 2}
qt = Poly(1, 't', 0, varsd)
qx = Poly(-1, 'y', 1, varsd)
qy = Poly(1, 'x', 1, varsd)
print("creating ContinuousReachability wrapper")
D = Reach(
    [b't', b'x', b'y'],
    [qt, qx, qy],
    [(0,0), (4,5), (1,2)],
    5,
    0.1,
    orders=[1, 7, 7],
)
print "t' = {}\nx' = {}\ny' = {}".format(qt, qx, qy)
print("running...")
resd = D.run()
statd = "ran successfully!" if 1 <= resd <= 3 else "failed!"
print "{} -- {} flowpipes computed".format(statd, D.num_flowpipes)
print("plotting...")
D.wplot(dict, b'x', b'y', b'resd')
