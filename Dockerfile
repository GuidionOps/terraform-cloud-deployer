FROM python:3.7.15

COPY . /application
RUN cd /application; pip install .
RUN apt-get update && \
    apt-get install -y jq && \
    rm -rf /var/lib/apt/lists/*

# We can't use ENTRYPOINT because CircleCI doesn't know how to handle this
# ENTRYPOINT ["/usr/local/bin/tfcd"]
