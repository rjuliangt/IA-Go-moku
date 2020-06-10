FROM tensorflow/tensorflow:2.0.0-py3

WORKDIR /home

COPY app .
RUN pip3 install --no-cache-dir -r requirements.txt
