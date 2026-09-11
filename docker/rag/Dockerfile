FROM ghcr.io/astral-sh/uv:0.12.10-python3.10-trixie


WORKDIR /app

# Install additional system dependencies for lxml and other packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libavif-dev pkg-config \
    libjpeg-dev \
    gcc unzip zip \
    python3-dev \
    libxml2-dev \
    libxslt1-dev \
    libffi-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY src/requirements.txt .

RUN uv pip install -r requirements.txt --system
## --system flag to install system dependencies
## --no-cache-dir flag to prevent caching of packages

COPY src/ . 
## . = ./app current dir

RUN mkdir -p /app/models/db_schemes/

COPY docker/rag/alembic.ini /app/models/db_schemes/minirag/alembic.ini
COPY docker/rag/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
