FROM python:3.8-slim

ENV BDR_REG_ROOT=/bdrreg \
    BDR_REG_APP=/bdrreg/bdr-registry \
    BDR_REG_PORT=8080

RUN mkdir -p $BDR_REG_ROOT/logs $BDR_REG_ROOT/static

RUN apt-get update \
 && apt-get install -y --no-install-recommends curl \
    netcat-traditional \
    vim \
    curl \
    sudo \
    python-dev-is-python3 \
    build-essential \
    libpq-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    libbz2-dev \
    libldap2-dev \
    libsasl2-dev

COPY . $BDR_REG_APP
WORKDIR $BDR_REG_APP

RUN pip install -r requirements.txt

ENTRYPOINT ["./docker-setup.sh"]
CMD ["run"]
