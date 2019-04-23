# import pstats
# import cProfile
#
# import flowstar.flowroots as fr  # NOQA
#
# if __name__ == '__main__':
#     cProfile.runctx('fr.work_without_intEval()', globals(), locals(),
#                     "profile_without_intEval.prof")
#     s = pstats.Stats('profile_without_intEval.prof')
#     s.strip_dirs().sort_stats("time").print_stats()
