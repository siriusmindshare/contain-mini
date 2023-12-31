
# FROM container-registry.oracle.com/os/oraclelinux:7-slim
FROM oraclelinux:7-slim
#FROM wvbirder/database-enterprise:12.2.0.1-slim
COPY --from=siriusmindshare/python-base-libs-non-jdk:latest / /
#RUN mkdir -p /dist
COPY dist /dist
ARG no_proxy

COPY siriusmindshare.repo /etc/yum.repos.d/

ENV JAVA_HOME=/usr/java/default \
  PATH=$PATH:/usr/java/default/bin \
  LANG=en_US.UTF-8 \
  LC_ALL=en_US.UTF-8
#try without install


ARG DATASCIENCE_HOME

RUN groupadd -g 1090 rsvp \
  && useradd -u 1090 -g rsvp -ms /bin/bash rsvp
COPY siriusmindshare.repo /etc/yum.repos.d/


RUN yum clean metadata \
  && yum clean all \
  && yum install -y oracle-instantclient19.3-basic oracle-instantclient19.3-sqlplus libgcc.x86_64 openssl.x86_64 jdk1.8.x86_64 python3.x86_64\
  && mkdir -p ${DATASCIENCE_HOME} \
  && python3 -m pip install --upgrade pip \
  && python3 -m pip install pyrsistent==0.16.0 \
  && python3 -m pip install --user --upgrade setuptools wheel \
  && python3 -m pip install -I /dist/*.whl

COPY ds_infra/pem/server.cer.pem /pem/server.cer.pem
COPY ds_infra/pem/server.key.pem /pem/server.key.pem
RUN chmod 644 /pem/server.cer.pem
RUN chmod 644 /pem/server.key.pem

RUN rm -r /dist/ \
  && mkdir -p /usr/local/product1/logs ${DATASCIENCE_HOME}/models ${DATASCIENCE_HOME}/datafiles  ${DATASCIENCE_HOME}/pem ${DATASCIENCE_HOME}/config \
  && rm -f /etc/yum.repos.d/responsys.repo \
  && export install_dir=$(pip show ds_infra | grep Location | cut -d " " -f2) \
  && cp ${install_dir}/ds_infra/*.ini ${DATASCIENCE_HOME}/config


COPY ./ds_infra/tests/ $DATASCIENCE_HOME/tests/

COPY ./ds_infra/ds_infra.env $DATASCIENCE_HOME/config

WORKDIR /$DATASCIENCE_HOME



ARG REST_PORT
EXPOSE ${REST_PORT}

CMD ["python3", "-m", "ds_infra.app"]


