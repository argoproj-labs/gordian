FROM python:3.7-stretch AS builder

USER root
RUN mkdir /rep
COPY . /rep
WORKDIR /rep
RUN apt-get update && apt-get install -y python3 python-pip build-essential python-setuptools
RUN pip3 wheel . --wheel-dir=/rep/wheels

FROM python:3.7-stretch
USER root
RUN apt-get update && apt-get install -y --no-install-recommends python3 python-pip python-setuptools && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY --from=builder /rep /rep
COPY docker-entrypoint.sh /docker-entrypoint.sh
WORKDIR /rep
RUN pip3 install --no-index --find-links=/rep/wheels .
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["gordian"]
