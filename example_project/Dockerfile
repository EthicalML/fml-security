from seldonio/mlserver:1.1.0.dev6-slim

COPY . /opt/mlserver/runtime
RUN pip install /opt/mlserver/runtime

CMD mlserver start /mnt/models
