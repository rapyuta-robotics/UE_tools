FROM ubuntu:20.04 
ARG ROSDISTRO="foxy"

WORKDIR /root

RUN apt update && apt upgrade -y

RUN mkdir UE_tools

COPY . UE_tools/

WORKDIR /root/UE_tools

# remove sudo to execute inside docker
RUN find BuildROS2 -type f | xargs sed -i 's/sudo //g' 

# install dependency
ENV DEBIAN_FRONTEND=noninteractive
RUN apt install -y python3 python3-pip git wget curl software-properties-common
RUN apt update
RUN pip3 install -r requirements.txt

# build base libs
RUN python3 build_install_codegen.py --type base --build --rosdistro $ROSDISTRO

# build base msgs
RUN python3 build_install_codegen.py --type pkgs --build --rosdistro $ROSDISTRO