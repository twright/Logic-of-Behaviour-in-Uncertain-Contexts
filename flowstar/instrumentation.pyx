from collections import defaultdict

cdef class AggregateMetric:
    def __init__(self):
        self._time_totals = defaultdict(float)
        self._count_totals = defaultdict(int)
        self.events = []

    def total_time(self, name):
        return self._time_totals[name]
    
    def total_count(self, name):
        return self._count_totals[name]
    
    def metric(self, name, count, elapsed):
        if name not in self.events:
            self.events.append(name)
        self._time_totals[name] += elapsed
        self._count_totals[name] += count
    
    def print(self):
        for event in self.events:
            print(f"ran \"{event}\" {self.total_count(event)} "
                  f"times in {self.total_time(event)}")


cdef class PrefixedAggregateMetric:
    def __init__(self, str prefix, object agg_metric):
        self.prefix = prefix
        self.agg_metric = agg_metric

    def _prefixed_name(self, name):
        return f"[{self.prefix}] -- {name}"

    def total_time(self, name):
        return self.agg_metric.total_time(self._prefixed_name(name))
    
    def total_count(self, name):
        return self.agg_metric.total_count(self._prefixed_name(name))

    def print(self):
        print(f"=== Metrics for prefix [{self.prefix}] ===")
        for event in self.events:
            print(f"ran \"{event}\" {self.total_count(event)} "
                  f"times in {self.total_time(event)}")


    @property
    def events(self):
        for event in self.agg_metric.events:
            pre, main = event.split(' -- ')
            pre = pre[1:-1]
            if pre == self.prefix:
                yield main

    def metric(self, name, count, elapsed):
        self.agg_metric.metric(self._prefixed_name(name), count, elapsed)