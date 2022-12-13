FROM python:3.7.15

COPY . /application
RUN cd /application; pip install .
# We can't use ENTRYPOINT because CircleCI doesn't know how to handle this
# ENTRYPOINT ["/usr/local/bin/tfcd"]
