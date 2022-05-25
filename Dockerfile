FROM cccs/assemblyline-v4-service-base:latest

ENV SERVICE_PATH windowsdefender.WindowsDefender

USER root

RUN dpkg --add-architecture i386
RUN apt-get update  \
    && apt-get -y install  \
      build-essential  \
      libc6-dev-i386  \
      gcc-multilib \
      libreadline-dev:i386 \
      cabextract  \
      libimage-exiftool-perl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/al_service
COPY . .

RUN pip3 install --no-cache-dir --user -r requirements.txt && rm -rf ~/.cache/pip

WORKDIR /opt/al_service/loadlibrary
RUN git clone https://github.com/taviso/loadlibrary .
RUN make
RUN mv /opt/al_service/loadlibrary/mpclient /opt/al_service/loadlibrary/mpclient_old
COPY mpclient .
RUN chmod +x /opt/al_service/loadlibrary/mpclient
RUN ls -l /opt/al_service/loadlibrary

WORKDIR /opt/al_service/loadlibrary
ADD https://go.microsoft.com/fwlink/?LinkID=121721&arch=x86 /opt/al_service/loadlibrary/mpam-fe.exe
RUN cabextract /opt/al_service/loadlibrary/mpam-fe.exe --directory ./engine
RUN ls -l /opt/al_service/loadlibrary/engine

USER assemblyline

RUN exiftool /opt/al_service/loadlibrary/engine/mpengine.dll
RUN /opt/al_service/loadlibrary/mpclient requirements.txt