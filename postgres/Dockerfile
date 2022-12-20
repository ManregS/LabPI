FROM debian:stable 

RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y software-properties-common apt-utils curl bzip2 procps wget gnupg python3-pip libxml2-dev libssl-dev libcurl4-openssl-dev vim gnupg1 gnupg2 && \
    apt-add-repository 'deb http://security.debian.org/debian-security stretch/updates main' && \
    apt-get update -y

RUN apt-get update && \
    apt-get install -y locales locales-all
    
ENV LC_ALL ru_RU.UTF-8
ENV LANG ru_RU.UTF-8
ENV LANGUAGE ru_RU.UTF-8
ENV TZ Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list && \ 
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -

RUN apt-get update && \ 
    apt-get install -y postgresql-14 postgresql-client-14 postgresql-contrib-14

USER postgres

RUN /etc/init.d/postgresql start && \
    psql --command "alter user postgres with password 'postgres';" && \
    psql --command "create database tool_rental_db;" && \
    psql --command "grant all privileges on database tool_rental_db to postgres;"

RUN echo "host all all 0.0.0.0/0 md5" >> /etc/postgresql/14/main/pg_hba.conf

RUN echo "listen_addresses='*'" >> /etc/postgresql/14/main/postgresql.conf

VOLUME ["/etc/postgresql", "/var/log/postgresql", "/var/lib/postgresql"]
