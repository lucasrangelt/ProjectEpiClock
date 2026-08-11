FROM mcr.microsoft.com/devcontainers/python:3.11
WORKDIR /app
# USER root
RUN rm -f /etc/apt/sources.list.d/yarn.list
RUN apt-get update && apt-get install -y curl unzip \
    libpq-dev \
    gcc \
	postgresql-client \
    && curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -rf awscliv2.zip ./aws \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# USER vscode