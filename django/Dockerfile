FROM python:3.11

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFER 1

COPY ./dockerTools/requirements.txt /usr/src/app/dockerTools/requirements.txt

RUN	apt-get update && apt-get install -y postgresql-client
RUN apt-get update && apt-get install -y iproute2 net-tools

RUN pip install --upgrade pip && \
	pip install -r /usr/src/app/dockerTools/requirements.txt
	
CMD ["/usr/src/app/dockerTools/entrypoint.sh"]


