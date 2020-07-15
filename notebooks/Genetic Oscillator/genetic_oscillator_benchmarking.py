import sys, os, warnings
from contextlib import contextmanager
import gc

sys.path.insert(0, "/home/twright/Documents/PhD/Notebooks")

@contextmanager
def pause_gc():
    gc.disable()
    yield
    gc.enable()
    gc.collect()


@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:  
            yield
        finally:
            sys.stdout = old_stdout


@contextmanager
def suppress_warnings():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        yield


from lbuc import *
from flowstar import *
from lbuc.bondcalculus import *


from sage.all import *


R, (x1,x2,x3,x4,x5,x6,x7,x8,x9) = PolynomialRing(RIF,
    [f'x{i+1}' for i in range(9)]).objgens()

y = vector([
    50*x3 - RIF('0.1')*x1*x6,
    100*x4 - x1*x2,
    RIF('0.1')*x1*x6 - 50*x3,
    x2*x6 - 100*x4,
    5*x3 + RIF('0.5')*x1 - 10*x5,
    50*x5 + 50*x3 + 100*x4 - x6*(RIF('0.1')*x1 + x2 + 2*x8 + 1),
    50*x4 + RIF('0.01')*x2 - RIF('0.5')*x7,
    RIF('0.5')*x7 - 2*x6*x8 + x9 - RIF('0.2')*x8,
    2*x6*x8 - x9,
])

y0 = [
    RIF('[0.98, 1.02]'),
    RIF('[1.28, 1.32]'),
    RIF('[0.08, 0.12]'),
    RIF('[0.08, 0.12]'), # x4
    RIF('[0.08, 0.12]'),
    RIF('[1.28, 1.32]'), # x6
    RIF('[2.48, 2.52]'),
    RIF('[0.58, 0.62]'),
    RIF('[1.28, 1.32]'),
]

system = System(R, R.gens(), y0, y)


@pause_gc()
def test_monitoring(prop, duration, **kwargs):
    t0 = time.perf_counter()
    sig = prop.signal_for_system(system,
    duration, order=4, step=0.003,
    precondition=1,
    estimation=1e-1,
    max_remainder_queue=250,
    integration_method=IntegrationMethod.ONLY_PICARD_SYMB,
    cutoff_threshold=1e-6,
    **kwargs)
    t1 = time.perf_counter()
    print(f"Run done in {t1 - t0} sec\noptions: {repr(kwargs)}")
    return t1 - t0, sig


import concurrent.futures as fut
import flowstar.instrumentation as instrumentation

thread_pool = fut.ThreadPoolExecutor(100)


def benchmark_prop(prop, duration, **kwargs):
    agg_metric = instrumentation.AggregateMetric()
    tim, sig = test_monitoring(prop, duration,
                               instrumentor=agg_metric,
                               print_timings=False, **kwargs)
    agg_metric.print()
    return sig, tim, agg_metric


from gi.repository import Notify
Notify.init("LBUC Benchmarking")


import pandas as pd


def total_time_for_key(inst, ks):
    if isinstance(ks, str):
        ks = [ks]

    return sum(inst.total_time(k)
               for k in ks)


def total_times(results, keys, keys_short=None):
    ress = [
        (r['result'] if 'result' in r else r['future'].result())
            for r in results
    ]
    if keys_short is None:
        keys_short = keys
    data = pd.DataFrame({
        short_key: [total_time_for_key(r[2], key) for r in ress]
        for short_key, key in zip(keys_short, keys)
    })
    data.insert(len(keys), 'Total',
                [r[1] for r in ress])
    return data