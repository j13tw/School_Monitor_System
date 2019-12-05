FROM ubuntu:16.04
MAINTAINER ZhengSheng j13tw@yahoo.com.tw

RUN apt-get update
RUN apt-get install -y software-properties-common
RUN add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
RUN apt-get install -y wget 
RUN apt-get install -y apt-utils
RUN wget https://packages.grafana.com/gpg.key
RUN apt-key add gpg.key
RUN apt-get install apt-transport-https
RUN apt-get update
RUN apt-get install -y grafana
COPY grafana.ini /etc/grafana/grafana.ini
RUN service grafana-server start
RUN update-rc.d grafana-server defaults
RUN echo "all done !"
EXPOSE 5000
CMD service grafana-server start && tail -f /dev/null