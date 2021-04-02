FROM ubuntu:20.04

RUN echo "**** install runtime packages ****"
RUN apt-get update
RUN apt-get install -y --no-install-recommends \
    dbus \
    fcitx-rime \
    fonts-wqy-microhei \
    jq \
    pandoc \
    libxkbcommon-x11-0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-xinerama0 \
    python3 \
    python3-xdg \
    ttf-wqy-zenhei \
    wget \
    xz-utils
RUN apt-get install -y --no-install-recommends curl
RUN apt-get install -y --no-install-recommends ca-certificates
RUN apt-get install -y --no-install-recommends python3-pip
RUN echo "**** install calibre ****"
RUN wget --no-check-certificate -nv -O- https://download.calibre-ebook.com/linux-installer.sh | sh /dev/stdin
RUN apt-get install -y --no-install-recommends libasound2 libnspr4 libnss3 libxss1 xdg-utils unzip libappindicator1 fonts-liberation
RUN apt-get -f install
RUN wget http://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && apt install -y --no-install-recommends ./google-chrome*.deb
RUN CHROME_VERSION=$(curl https://chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
    wget https://chromedriver.storage.googleapis.com/$CHROME_VERSION/chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip && mv chromedriver /usr/bin/chromedriver && chown root:root /usr/bin/chromedriver && chmod +x /usr/bin/chromedriver

COPY /app /app
RUN cd /app/Articles && pip3 install -r requirements.txt

EXPOSE 80

CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "80"]
