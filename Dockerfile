FROM python:3.7.15

COPY . /application
RUN cd /application; pip install .
ENTRYPOINT ["/usr/local/bin/tfcd"]
