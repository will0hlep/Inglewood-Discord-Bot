FROM python:3.14.3
RUN pip install --upgrade pip
RUN pip install mcstatus discord==2.7.0 pytz==2025.2
CMD [ "python3", "/app/inglewood.py"]