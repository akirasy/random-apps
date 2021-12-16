FROM debian:buster

WORKDIR /root
ENV TZ="Asia/Kuala_Lumpur"

COPY . .

RUN apt update && apt install -y --no-install-recommends python3-pip python3-setuptools mplayer
RUN pip3 install --no-cache-dir -r requirements.txt

CMD [ "python3", "./muazzin.py"]
