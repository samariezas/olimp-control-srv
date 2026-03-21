FROM python:3.13-slim
WORKDIR /ctrl/app

RUN pip install --no-cache-dir --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd -ms /bin/bash ctrl
COPY . .
EXPOSE 8000
CMD ["/ctrl/app/prod_entrypoint.sh"]
