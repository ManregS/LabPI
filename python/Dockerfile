FROM debian:stable

RUN apt-get update -y && \
    apt-get install -y software-properties-common apt-utils bzip2 procps wget  && \
    apt-add-repository 'deb http://security.debian.org/debian-security stretch/updates main' 

RUN apt-get update && \
    apt-get install -y locales locales-all
    
ENV LC_ALL ru_RU.UTF-8
ENV LANG ru_RU.UTF-8
ENV LANGUAGE ru_RU.UTF-8
ENV TZ Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get install git -y

RUN adduser --disabled-password --gecos '' user
USER user
WORKDIR /home/user

RUN wget \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh 
RUN /home/user/miniconda3/condabin/conda init bash
RUN /home/user/miniconda3/condabin/conda create -n python -c conda-forge openssl python=3.8
SHELL ["/home/user/miniconda3/condabin/conda", "run", "-n", "python", "/bin/bash", "-c"]
RUN echo 'conda activate python' >> /home/user/.bashrc

ENV PATH $PATH:/home/user/miniconda3/bin 

RUN pip install pandas --no-cache-dir
RUN pip install shiny --no-cache-dir
RUN pip install psycopg2-binary --no-cache-dir
