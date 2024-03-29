ARG UBUNTU_VER="22.04"

FROM ubuntu:${UBUNTU_VER} 
ARG ROSDISTRO="humble"

RUN apt update && apt install sudo

RUN adduser --disabled-password --gecos '' admin && \
    adduser admin sudo && \
    echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER admin
WORKDIR /home/admin

RUN mkdir UE_tools

COPY --chown=admin:admin . UE_tools/

WORKDIR /home/admin/UE_tools

# install dependency
ENV DEBIAN_FRONTEND=noninteractive
RUN sudo apt install -y tzdata && \
    sudo apt install -y python3 python3-pip git wget curl software-properties-common && \
    sudo pip3 install -r requirements.txt

# build base libs and msgs
RUN python3 build_install_codegen.py --type base --build --rosdistro $ROSDISTRO && \
    python3 build_install_codegen.py --type pkgs --build --rosdistro $ROSDISTRO && \
    rm -r ros2_ws/src ros2_ws/build ros2_ws/log


ADD entrypoint.sh /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]