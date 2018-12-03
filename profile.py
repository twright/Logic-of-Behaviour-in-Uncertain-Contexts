import pstats, cProfile
# import pyximport
# pyximport.install()

import flowstar.flowroots as fr

# cProfile.runctx('fr.work()', globals(), locals(), "profile.prof")
# s = pstats.Stats('profile.prof')
# s.strip_dirs().sort_stats("time").print_stats()
cProfile.runctx('fr.work_without_intEval()', globals(), locals(), "profile_without_intEval.prof")
s = pstats.Stats('profile_without_intEval.prof')
s.strip_dirs().sort_stats("time").print_stats()
