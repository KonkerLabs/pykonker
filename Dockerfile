# FROM alpine as base
FROM amancevice/pandas:1.0.1-alpine as base

RUN apk update \
    && apk add --no-cache \
        bash \
        python3 \
        build-base \
	libressl-dev \
	libffi-dev \
        python3-dev \
        openssh \
        ca-certificates \
        groff \
        git \
        zip \
        git-subtree \
        jq \
        unzip \
        busybox-extras \
    && pip3 install --upgrade pip \
    && python3 -m pip install \
        pylint \
        boto3 \
        jinja2 \
        twine \
        awscli \
        oauthlib \
        requests-oauthlib \
        arrow \
    && rm -rf /opt/build/* \
    && rm -rf /var/cache/apk/* \
    && rm -rf /root/.cache/* \
    && rm -rf /tmp/*

FROM scratch as user
COPY --from=base . .

# RUN python3 -m pip install -r requirements.txt 

ARG HOST_UID=${HOST_UID:-4000}
ARG HOST_USER=${HOST_USER:-nodummy}

RUN [ "${HOST_USER}" == "root" ] || \
    (adduser -h /home/${HOST_USER} -D -u ${HOST_UID} ${HOST_USER} \
    && chown -R "${HOST_UID}:${HOST_UID}" /home/${HOST_USER})

USER ${HOST_USER}
WORKDIR /home/${HOST_USER}
COPY files/profile .profile
