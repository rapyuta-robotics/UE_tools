FROM ubuntu:20.04 
ARG ROSDISTRO="humble"

RUN apt update && apt upgrade -y

COPY . UE_tools/

WORKDIR UE_tools

RUN rm -r BuildROS2/ros2_ws || true

# remove sudo to execute inside docker
RUN find . -type f | xargs sed -i 's/sudo //g' 

# install dependency
ENV DEBIAN_FRONTEND=noninteractive
RUN apt install -y python3 python3-pip git wget curl software-properties-common
RUN apt update
RUN pip3 install -r requirements.txt

RUN python3 build_install_codegen.py --type base --build --config --rosdistro $ROSDISTRO