FROM python:3.8.10
ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
CMD ./donsar_system/manage.py runserver 0.0.0.0:8001
EXPOSE 8001