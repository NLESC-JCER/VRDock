FROM python:3.9.12

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir tornado

COPY ./ .

ENTRYPOINT [ "python", "server.py" ]