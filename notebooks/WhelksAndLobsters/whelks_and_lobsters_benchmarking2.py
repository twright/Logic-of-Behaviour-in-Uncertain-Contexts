import sys, os, warnings
from contextlib import contextmanager
import gc
import concurrent.futures as fut
import flowstar.instrumentation as instrumentation
import pandas as pd
import copy


from gi.repository import Notify
Notify.init("LBUC Benchmarking")


from lbuc import *
from flowstar import *
from lbuc.bondcalculus import *


pool = fut.ProcessPoolExecutor(3)
thread_pool = fut.ThreadPoolExecutor(100)
#management_pool = fut.ThreadPoolExecutor(1)
exec_pool = fut.ThreadPoolExecutor(1)

pools = dict()


def restart_pool():
    global pool
    
    del pool
    pool = fut.ProcessPoolExecutor(4)

def cleanup_after_tasks(name, tasks):
    fut.wait(tasks)
    pools[name].shutdown()

def _schedule_tests(name, prop, depth, **kwargs):
    with fut.ProcessPoolExecutor(3) as pool:
        return [
            schedule_test(f"{name}depth{n}", prop, n, pool, **kwargs)
            for n in range(depth)
        ]

def schedule_tests(name, prop, depth, **kwargs):
    return exec_pool.submit()
    pools[name] = fut.ProcessPoolExecutor(3)

    ress = [
        schedule_test(f"{name}depth{n}", prop, n, pool=pools[name], **kwargs)
        for n in range(depth)
    ]
    thread_pool.submit(cleanup_after_tasks, name, futures(ress))
    

def _test_histogram_search(pool, name, prop, depth, **kwargs):
    return pool.submit(test_histogram_search, name, prop, depth, **kwargs).result()

def schedule_test(name, prop, depth, pool, **kwargs):
    return {
        'prop': prop,
        'depth': depth,
        'kwargs': kwargs,
        'future': pool.submit(test_histogram_search, name, prop, depth, **kwargs),
    }


def notify_when_done(ress, task_description=None):
    fut.wait(futures(ress))
    
    if task_description is None:
        Notify.Notification.new("Benchmark run done!").show()
    else:
        Notify.Notification.new("Benchmark run done!",
                                task_description).show()


def futures(results):
    return [res['future'] for res in results]


def gen_results(n, *args, task_description=None, **kwargs):
    results = [
        schedule_test(*args, **kwargs)
            for _ in range(n)
    ]
    thread_pool.submit(notify_when_done, results, task_description)
    return results


gen_results_pool = fut.ThreadPoolExecutor(1)


def gen_results_managed(*args, warmup=0, **kwargs):
    results = gen_results(*args, **kwargs)
    fut.wait(futures(results))
    for r in results:
        r['result'] = r['future'].result()
        del r['future']
    return results[warmup:]


def gen_results_async(*args, **kwargs):
    return gen_results_pool.submit(gen_results_managed,
                                   *args, **kwargs)


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



import sage.all as sg


k = 0.8; b = 0.6; c = 0.3; e = 0.05; f = 2

m = BondModel("WhelksAndLobsters.bond")

s = m.process("[0, 1.4] Whelk || [0, 8] Lobster with network N(0.8, 0.6, 0.3, 0.05, 2)").as_system
s2 = m.process("[1, 1.2] Whelk || [4, 6] Lobster with network N(0.8, 0.6, 0.3, 0.05, 2)").as_system

@pause_gc()
def test_histogram_search(name, prop, depth, plot=True, **kwargs):
    agg_metric = instrumentation.AggregateMetric()
    t0 = time.perf_counter()
    csig = prop.context_signal_for_system(s, 0, instrumentor=agg_metric, **kwargs)
    # Example the tree to desired depth (but ignore the result)
    # to make sure all of the computation gets done now
    # csig.histogram2d(depth)
    list(csig.expand_signals(depth))
    t1 = time.perf_counter()
    print(f"Run {name} done in {t1 - t0} sec")
    metric_after_run = copy.deepcopy(agg_metric)
    if plot:
        plot = csig.plot_histogram2d(depth, flip=True)
        plot.save(f"output/{name}.pdf")
        t2 = time.perf_counter()
        print(f"Plot {name} done in {t2 - t1} sec")

    return t1 - t0, metric_after_run


@pause_gc()
def test_signal_refinement(name, prop, t, depth, **kwargs):
    agg_metric = instrumentation.AggregateMetric()
    t0 = time.perf_counter()
    csig = prop.context_signal_for_system(s2, t, instrumentor=agg_metric, **kwargs)
    # Example the tree to desired depth (but ignore the result)
    # to make sure all of the computation gets done now
    # csig.histogram2d(depth)
    sig = csig.refined_signal(depth)
    t1 = time.perf_counter()
    print(f"Run {name} done in {t1 - t0} sec")

    return t1 - t0, sig, agg_metric


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