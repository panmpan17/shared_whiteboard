FROM python:3
EXPOSE 31085
RUN pip3 install git+https://github.com/dpallot/simple-websocket-server.git
RUN pip3 install requests
COPY . .
CMD python3 server.py -port 31085 -online True