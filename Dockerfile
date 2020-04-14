FROM python:3.8.2-alpine
MAINTAINER suspect22

ENV PYTHONUNBUFFERED 1
ENV PROJECTPATH /app
ENV PYTHONUSER pythonenvuser
ENV PROJECTSOURCE ./app/
ENV EXPOSEPORT 8000
ENV VOLUMESDIR /vol/web/
ENV MEDIADIR ${VOLUMESDIR}media
ENV STATICDIR ${VOLUMESDIR}static

COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache postgresql-client jpeg-dev \
    && apk add --update --nocache --virtual .tmp-build-deps \
        gcc libc-dev linux-headers postgresql-dev \
        musl-dev zlib zlib-dev jpeg-dev \
    && pip install -r /requirements.txt \
    && mkdir -p ${MEDIADIR} \
    && mkdir -p ${STATICDIR} \
    && adduser -D ${PYTHONUSER} \
    && chown -R ${PYTHONUSER}.${PYTHONUSER} ${VOLUMESDIR} \
    && chmod -R 755 ${VOLUMESDIR} \
    && mkdir ${PROJECTPATH} \
    && apk del .tmp-build-deps
WORKDIR ${PROJECTPATH}
COPY ${PROJECTSOURCE} ${PROJECTPATH}

USER ${PYTHONUSER}

EXPOSE ${EXPOSEPORT}/udp
EXPOSE ${EXPOSEPORT}/tcp