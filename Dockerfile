FROM python:3.8

WORKDIR /code

COPY requirements.txt .
RUN pip install --user -r requirements.txt

RUN apt-get update
RUN apt-get install -y unzip xvfb libxi6 libgconf-2-4

RUN curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add
RUN echo "deb [arch=amd64]  http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
RUN apt-get -y update
RUN apt-get -y install google-chrome-stable

RUN wget https://chromedriver.storage.googleapis.com/2.41/chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip

#RUN mv chromedriver /usr/bin/chromedriver
RUN chown root:root chromedriver
RUN chmod +x chromedriver

COPY ./src .

# update PATH environment variable
ENV PATH=/root/.local:$PATH

CMD [ "python3", "main.py" ]
