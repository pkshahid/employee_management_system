FROM python:3.10

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirments.txt .

RUN pip install -r requirments.txt


ENTRYPOINT [ "./docker-entrypoint.sh" ]

COPY . .
