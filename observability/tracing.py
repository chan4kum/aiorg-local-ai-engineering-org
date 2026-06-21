from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
import os

def setup_tracing(service_name: str = "openclaw"):
    resource = Resource(attributes={
        SERVICE_NAME: service_name
    })

    provider = TracerProvider(resource=resource)
    
    # Configure OTLP Exporter - using env var for endpoint if available
    otlp_endpoint = os.getenv("OTLP_ENDPOINT", "http://localhost:4317")
    exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
    
    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)
    
    trace.set_tracer_provider(provider)
    
    return provider
