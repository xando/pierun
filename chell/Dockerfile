FROM ubuntu:14.04

RUN apt-get update
RUN apt-get install openssh-server -y
RUN apt-get install python-pip python-dev git-core libpq-dev -y
RUN pip install -U pip

RUN mkdir /var/run/sshd
RUN echo 'root:test' |chpasswd

RUN locale-gen pl_PL.UTF-8 en_GB.UTF-8

RUN echo 'export PS1="(\[\e[34m\]v\[\e[m\]:\[\e[32m\]**NAME**\[\e[m\]) \w: "' > /root/.bashrc

RUN echo "alias l='ls -a'" >> /root/.bashrc
RUN echo "alias ll='ls -l'" >> /root/.bashrc
RUN echo "alias la='ls -la'" >> /root/.bashrc

RUN sed -ri 's/^session\s+required\s+pam_loginuid.so$/session optional pam_loginuid.so/' /etc/pam.d/sshd
RUN touch /root/.hushlogin

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D","-o", "UseDNS=no", "-o", "PermitRootLogin=yes", "-o", "StrictModes=no", "-E", "/var/log/auth.log"]

