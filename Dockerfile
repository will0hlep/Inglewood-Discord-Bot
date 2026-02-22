FROM python:3.14.2
RUN pip install --upgrade pip
RUN pip install mcstatus discord pytz
CMD [ "python3", "/app/inglewood.py"]
