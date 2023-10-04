FROM python:3.9-bookworm AS builder

USER root
RUN mkdir /rep
COPY . /rep
WORKDIR /rep
RUN apt-get update && apt-get install -y python3 python3-pip build-essential
RUN pip3 wheel . --wheel-dir=/rep/wheels
RUN pip3 install setuptools

FROM python:3.9-bookworm
USER root
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN pip3 install setuptools

COPY --from=builder /rep /rep
COPY docker-entrypoint.sh /docker-entrypoint.sh
WORKDIR /rep
RUN pip3 install --no-index --find-links=/rep/wheels .
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["gordian"]
