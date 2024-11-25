FROM python:3.12
WORKDIR /src
ADD . /src
RUN pip install -r requirements.txt
CMD ["python", "-u", "main.py"]
