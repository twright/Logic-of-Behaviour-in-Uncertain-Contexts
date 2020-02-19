from collections import defaultdict

cdef class AggregateMetric:
    def __init__(self):
        self._time_totals = defaultdict(float)
        self._count_totals = defaultdict(int)
        self._metrics = set()
        
    def total_time(self, name):
        return self._time_totals[name]
    
    def total_count(self, name):
        return self._count_totals[name]
    
    def metric(self, name, count, elapsed):
        self._metrics.add(name)
        self._time_totals[name] += elapsed
        self._count_totals[name] += count
    
    def print(self):
        for metric in self._metrics:
            print(f"ran \"{metric}\" {self.total_count(metric)} "
                  f"times in {self.total_time(metric)}")