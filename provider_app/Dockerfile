from python:3.8-alpine3.11

ARG USERGROUP=app
ARG USERNAME=app
ARG USERID=1001

EXPOSE 5000

RUN addgroup ${USERGROUP}
RUN adduser ${USERNAME} --disabled-password -u ${USERID} -G ${USERGROUP}



WORKDIR /${USERNAME}/

# install python globally
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt --no-cache
RUN rm requirements.txt

RUN pip install -U gunicorn

ADD app.py app.py
ADD wsgi.py wsgi.py
ADD static static

USER ${USERNAME}

ENV PYTHONPATH=/app/

# as non-root user the usage of port 80 is not allowed ;(
CMD gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app