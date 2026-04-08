# All-in-one image: FreeLing 4.2 + Flask/gunicorn service
# Based on Ubuntu 20.04 (Focal) — last distro with official FreeLing .deb support
# Python 3.9 via deadsnakes PPA (spaCy pinned <3.8 to stay compatible)
FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
ENV FREELINGSHARE=/usr/share/freeling

# Generate en_US.UTF-8 locale (required by FreeLing)
RUN apt-get update && apt-get install -y --no-install-recommends locales \
    && locale-gen en_US.UTF-8 \
    && rm -rf /var/lib/apt/lists/*
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

# System dependencies (including libboost needed by FreeLing)
# + deadsnakes PPA for Python 3.11
RUN apt-get update && apt-get install -y --no-install-recommends \
        wget ca-certificates software-properties-common \
        build-essential \
        libboost-filesystem1.71.0 \
        libboost-program-options1.71.0 \
        libboost-regex1.71.0 \
        libboost-system1.71.0 \
        libboost-thread1.71.0 \
        libicu66 \
        libfoma0 \
    && add-apt-repository -y ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y --no-install-recommends \
        python3.9 python3.9-venv python3.9-dev \
    && rm -rf /var/lib/apt/lists/*

# Install FreeLing 4.2 from GitHub releases
RUN wget -q https://github.com/TALP-UPC/FreeLing/releases/download/4.2/freeling-4.2-focal-amd64.deb \
    && wget -q https://github.com/TALP-UPC/FreeLing/releases/download/4.2/freeling-langs-4.2.deb \
    && dpkg -i freeling-4.2-focal-amd64.deb freeling-langs-4.2.deb || true \
    && apt-get update && apt-get install -y -f --no-install-recommends \
    && rm -f freeling-4.2-focal-amd64.deb freeling-langs-4.2.deb \
    && rm -rf /var/lib/apt/lists/*

# Python virtualenv with 3.11
RUN python3.9 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy models
RUN python -m spacy download en_core_web_sm \
    && python -m spacy download fr_core_news_sm \
    && python -m spacy download de_core_news_sm \
    && python -m spacy download it_core_news_sm \
    && python -m spacy download pt_core_news_sm

# Copy FreeLing config overrides
COPY config/ /usr/share/freeling/config/

# Copy application source
COPY app.py formatters.py wsgi.py analyzer.cfg ./
COPY analyzers/ analyzers/
COPY templates/ templates/

# Copy entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 5000
EXPOSE 9999

ENTRYPOINT ["/entrypoint.sh"]
