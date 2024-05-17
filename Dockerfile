FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install -y openssh-server git uuid-runtime
RUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

RUN useradd -m -s /bin/bash bilbo
RUN echo "bilbo:bilbo" | chpasswd

COPY .bash_profile /home/bilbo/.bash_profile
USER bilbo
RUN git clone https://github.com/apetro/BashVenture.git /home/bilbo/BashVenture
RUN chmod +x /home/bilbo/BashVenture/adventure.sh

USER root
EXPOSE 22
ENTRYPOINT service ssh start && bash

