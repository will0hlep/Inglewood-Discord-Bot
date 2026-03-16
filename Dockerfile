ARG PYTHONVERSION
FROM python:$PYTHONVERSION
RUN pip3 install --upgrade pip
RUN pip3 install discord.py==2.7.1 mcstatus==13.0.0 pytz==2025.2
WORKDIR /app
CMD [ "python3", "inglewood.py"]