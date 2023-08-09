FROM python:3-slim

ENV LANG="C.UTF-8" \
    LC_ALL="C.UTF-8" \
    PATH="/home/python/.rye/shims:$PATH" \
    PIP_NO_CACHE_DIR="false"

ENV RYE_VERSION="0.10.0" \
    RYE_INSTALL_OPTION="--yes"

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    inotify-tools \
    make \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --gid 1000 python && \
    useradd  --uid 1000 --gid python --shell /bin/bash --create-home python

USER 1000
WORKDIR /home/python/

RUN curl -sSf https://rye-up.com/get | bash -

COPY --chown=python:python . /home/python
WORKDIR /home/python/code

RUN rye config --set-bool behavior.global-python=true
RUN rye sync

CMD ["rye", "run", "python"]
