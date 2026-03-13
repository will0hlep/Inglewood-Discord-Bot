ARG PYTHONVERSION
WORKDIR /app
FROM python:$PYTHONVERSION
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
CMD [ "python3", "inglewood.py"]