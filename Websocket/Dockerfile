FROM python:3
EXPOSE 21085
RUN pip3 install git+https://github.com/dpallot/simple-websocket-server.git
COPY server.py server.py
CMD python3 server.py