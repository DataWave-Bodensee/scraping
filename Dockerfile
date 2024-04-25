FROM python:3.12-slim

WORKDIR /scraper

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "scraper.py"]