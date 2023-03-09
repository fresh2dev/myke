ARG HB_IMAGE_REGISTRY=docker.io
FROM ${HB_IMAGE_REGISTRY}/python:3.10.10-slim-bullseye
RUN apt-get update && apt-get install -y build-essential
ENV PYTHONUNBUFFERED=1
RUN pip install --upgrade pip setuptools wheel
COPY ./dist /dist
RUN find /dist -name "*.whl" -exec pip install "{}[extras,build,docs,dev,tests]" \;
ENTRYPOINT ["myke"]
