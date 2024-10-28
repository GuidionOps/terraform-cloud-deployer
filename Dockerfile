FROM python:3.12.2

COPY . /application
RUN cd /application; pip install .
RUN apt-get update && \
    apt-get install -y jq gnupg software-properties-common && \
    wget -O- https://apt.releases.hashicorp.com/gpg | apt-key add - && \
    echo "deb https://apt.releases.hashicorp.com $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/hashicorp.list && \
    apt-get update && \
    apt-get install -y terraform=1.6.1-1 zip && \
    rm -rf /var/lib/apt/lists/*

# We can't use ENTRYPOINT because CircleCI doesn't know how to handle this
# ENTRYPOINT ["/usr/local/bin/tfcd"]
