from prometheus_client import Counter, Histogram
REQS = Counter("rag_requests_total", "Total /answer requests")
ERRS = Counter("rag_errors_total", "Total errors in /answer")
LAT  = Histogram("rag_answer_latency_seconds", "Latency for /answer in seconds", buckets=(0.1,0.25,0.5,1,2,5,10))
def record_request(): REQS.inc()
def record_error(): ERRS.inc()
def observe_latency(seconds: float): LAT.observe(seconds)
