from __future__ import print_function
# absolute_import,

from sage.all import RIF, QQ
import sage.all as sage

R, (x,y) = sage.PolynomialRing(QQ, 'x, y').objgens()
from ulbc import *
us = [x,y]
k=RIF(0.8); b=RIF(0.6); c=RIF(0.3); e=RIF(0.05); f=RIF(2)
vf = sage.vector([b*x*(RIF(1)-x) - c*x*(k-x)*y,
                  -e*y*(RIF(1)+y)+f*x*(k-x)*y])
v0 = [RIF(0.5), RIF(2.0)]
v1 = [RIF(0.4), RIF(2.5)]
v2 = [RIF(1,1.2), RIF(4,6)]
v3 = v2

P = Atomic((x - 1)**2 + y**2 - 0.2)

def work5():
    return F(RIF(4, 4.5), P).signal_for_system(vf, v3, 5, order=5, step=0.01,
                    precondition=1,
                    estimation=1e-3,
                    integrationScheme=2,
                    cutoff_threshold=1e-5,
                    tentative_unpreconditioning=True,
                    symbolic_composition=True,
                    use_masks=True)

print(work5())