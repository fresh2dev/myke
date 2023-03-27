ARG HB_IMAGE_REGISTRY=docker.io
FROM ${HB_IMAGE_REGISTRY}/python:3.10.10-slim-bullseye
LABEL org.opencontainers.image.source=https://www.github.com/fresh2dev/myke
LABEL org.opencontainers.image.description="None"
LABEL org.opencontainers.image.licenses=GPLv3
RUN apt-get update && apt-get install -y build-essential git
ENV PYTHONUNBUFFERED=1
RUN pip install --upgrade pip setuptools wheel
COPY ./dist /dist
RUN find /dist -name "*.whl" -exec pip install "{}[extras,build,docs,dev,tests]" \;
ENTRYPOINT ["myke"]
