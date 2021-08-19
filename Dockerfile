FROM python:3.7-slim
RUN pip install tweepy
RUN pip install pytz
RUN pip install google-cloud-pubsub
WORKDIR /capstone
COPY . .
ENV PYTHONPATH="."
CMD ["TwitterPublisher.py","intense-palace-322723","capstone-topic2"]
ENTRYPOINT ["python3"]

