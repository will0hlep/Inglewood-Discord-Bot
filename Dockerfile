ARG PYTHONVERSION
FROM python:$PYTHONVERSION
RUN pip install --upgrade pip
WORKDIR /app
RUN pip3 install -r /requirements.txt
CMD [ "python3", "/inglewood.py"]