from genetic_oscillator_benchmarking import *

import concurrent.futures as fut
import flowstar.instrumentation as instrumentation

pool = fut.ProcessPoolExecutor(7)

thread_pool = fut.ThreadPoolExecutor(100)


def restart_pool():
    global pool
    
    del pool
    pool = fut.ProcessPoolExecutor(4)


def schedule_test(prop, duration, **kwargs):
    return {
        'prop': prop,
        'duration': duration,
        'kwargs': kwargs,
        'future': pool.submit(
            benchmark_prop, prop, duration, **kwargs),
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