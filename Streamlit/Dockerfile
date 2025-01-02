FROM python:3.9-slim

WORKDIR /app2

COPY requirements.txt /app2/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app2

EXPOSE 8501
CMD ["treamlit", "run", "app.py"]
