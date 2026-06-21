from prometheus_client import Counter, Histogram, Gauge

# Define metrics
LLM_CALLS_TOTAL = Counter(
    'llm_calls_total',
    'Total number of LLM API calls',
    ['model', 'status']
)

LLM_TOKENS_TOTAL = Counter(
    'llm_tokens_total',
    'Total tokens used in LLM calls',
    ['model', 'token_type'] # token_type: prompt, completion, total
)

LLM_COST_TOTAL = Counter(
    'llm_cost_total',
    'Total estimated cost of LLM calls in USD',
    ['model']
)

LLM_LATENCY_SECONDS = Histogram(
    'llm_latency_seconds',
    'Latency of LLM API calls',
    ['model'],
    buckets=[0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0]
)

TASK_PROCESSING_LATENCY = Histogram(
    'task_processing_latency_seconds',
    'Time taken to process a task from start to finish',
    ['workflow_type', 'status']
)

ACTIVE_AGENTS = Gauge(
    'active_agents_total',
    'Number of currently active agents',
    ['role']
)

EVENT_BUS_MESSAGES_TOTAL = Counter(
    'event_bus_messages_total',
    'Total messages processed via event bus',
    ['stream', 'status']
)

def record_llm_call(model: str, prompt_tokens: int, completion_tokens: int, cost: float, duration: float, success: bool = True):
    status = "success" if success else "error"
    LLM_CALLS_TOTAL.labels(model=model, status=status).inc()
    
    if success:
        LLM_TOKENS_TOTAL.labels(model=model, token_type="prompt").inc(prompt_tokens)
        LLM_TOKENS_TOTAL.labels(model=model, token_type="completion").inc(completion_tokens)
        LLM_TOKENS_TOTAL.labels(model=model, token_type="total").inc(prompt_tokens + completion_tokens)
        LLM_COST_TOTAL.labels(model=model).inc(cost)
        LLM_LATENCY_SECONDS.labels(model=model).observe(duration)
