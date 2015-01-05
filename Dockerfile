FROM makinacorpus/pythonbox
MAINTAINER Makina Corpus "python@makina-corpus.com"

#
#  Converters binaries
#...
RUN apt-get install -y libreoffice unoconv inkscape rabbitmq-server

#
#  ConvertIt
#...
# Recursive copy of repository
ADD . /opt/apps/convertit
# Replace repo with https
RUN (cd /opt/apps/convertit && git remote rm origin)
RUN (cd /opt/apps/convertit && git remote add origin https://github.com/makinacorpus/convertit.git)
# Install
RUN (cd /opt/apps/convertit && make install)
RUN /opt/apps/convertit/bin/pip install gunicorn
ADD .docker/run.sh /usr/local/bin/run

#
#  Run !
#...
EXPOSE 6543
CMD ["/bin/sh", "-e", "/usr/local/bin/run"]
