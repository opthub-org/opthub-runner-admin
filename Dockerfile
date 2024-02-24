FROM python:3.9

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY . /usr/src/app
RUN pip3 install -e .

ENTRYPOINT ["opthub-evaluator"]
