FROM python:3
EXPOSE 8000
EXPOSE 80
RUN pip3 install git+https://github.com/dpallot/simple-websocket-server.git
COPY . .
CMD python3 server.py