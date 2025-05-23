FROM ubuntu:22.04

ENV DEBIAN_FRONTEND noninteractive

RUN apt update && \
    apt upgrade -y && \
    apt install -y build-essential gdb lcov pkg-config \
                   libbz2-dev libffi-dev libgdbm-dev libgdbm-compat-dev liblzma-dev \
                   libncurses5-dev libreadline6-dev libsqlite3-dev libssl-dev \
                   lzma lzma-dev tk-dev uuid-dev zlib1g-dev wget unzip libaio1
        
#  clean up
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python 3.11.3
RUN wget https://www.python.org/ftp/python/3.11.3/Python-3.11.3.tgz && \
    tar -xvf Python-3.11.3.tgz && \
    cd Python-3.11.3 && \
    ./configure --enable-optimizations --enable-profiling --with-lto --with-threads && \
    make -j $(nproc) && \
    make altinstall && \
    cd .. && \
    rm -rf Python-3.11.3 && \
    rm Python-3.11.3.tgz


RUN mkdir /product_service
COPY . /product_service/
WORKDIR /product_service/

# 複製需求文件
COPY requirements.txt .


# env
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV TZ=Asia/Taipei


# mount 在 product_service
VOLUME /product_service 

RUN ln -s /usr/local/bin/python3.11 /usr/local/bin/python3 && \
    ln -s /usr/local/bin/python3.11 /usr/local/bin/python && \
    ln -s /usr/local/bin/pip3.11 /usr/local/bin/pip3 && \
    ln -s /usr/local/bin/pip3.11 /usr/local/bin/pip
    

# install package
# 安裝需求
RUN pip install -r requirements.txt


# 開放 port 8000
EXPOSE 8000


CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

