FROM python:3.14.3
RUN pip install --upgrade pip
RUN pip install mcstatus==13.0.0 discord.py==2.7.1 pytz==2025.2
CMD [ "python3", "/app/inglewood.py"]