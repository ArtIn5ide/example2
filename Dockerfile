FROM python:3.8-slim
RUN mkdir /EST
COPY . /EST
WORKDIR /EST
RUN pip install -q schedule==0.6.0 requests==2.21.0

CMD [ "python","packages/refresh.py" ]
