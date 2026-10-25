FROM python:3.11-slim
RUN pip install --no-cache-dir numpy==1.26.4
ENV OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
WORKDIR /app
COPY worker.py /app/worker.py
USER 65534:65534
ENTRYPOINT ["python", "-I", "/app/worker.py"]
