import opentracing
from opentracing.ext import globaltracer

print globaltracer.get()
globaltracer.register(opentracing.Tracer())
print globaltracer.get()
print globaltracer.get().start_span('hola')

