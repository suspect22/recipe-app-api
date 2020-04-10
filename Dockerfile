FROM python:3.8.2-alpine
MAINTAINER suspect22

ENV PYTHONUNBUFFERED 1
ENV PROJECTPATH /app
ENV PYTHONUSER pythonenvuser
ENV PROJECTSOURCE ./app/
ENV EXPOSEPORT 8000

COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache postgresql-client \ 
    && apk add --update --nocache --virtual .tmp-build-deps \
        gcc libc-dev linux-headers postgresql-dev \
    && pip install -r /requirements.txt \
    && mkdir ${PROJECTPATH} \
    && adduser -D ${PYTHONUSER} \
    && apk del .tmp-build-deps
WORKDIR ${PROJECTPATH}
COPY ${PROJECTSOURCE} ${PROJECTPATH}

USER ${PYTHONUSER}

EXPOSE ${EXPOSEPORT}/udp
EXPOSE ${EXPOSEPORT}/tcp