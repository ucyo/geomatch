FROM python:3-slim as builder

ENV LANG="C.UTF-8" \
    LC_ALL="C.UTF-8" \
    PATH="/home/python/.rye/shims:$PATH" \
    PIP_NO_CACHE_DIR="false"

ENV RYE_VERSION="0.11.0" \
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

COPY --chown=python:python ./code /home/python/code
WORKDIR /home/python/code

RUN rye config --set-bool behavior.global-python=true
RUN rye sync

# Needs to be added for numba to find the libsvm library
# Check if it worked with `rye run numba -s`. It should look like following:
# __SVML Information__
# SVML State, config.USING_SVML                 : True
# SVML Library Loaded                           : True
# llvmlite Using SVML Patched LLVM              : True
# SVML Operational                              : True
ENV LD_LIBRARY_PATH="/home/python/code/.venv/lib/" \
    PATH="/home/python/.local/bin:$PATH"

RUN mkdir dist && rye build --wheel --clean

FROM python:3-slim as prod
COPY --from=builder /home/python/code/dist /dist
ENV LD_LIBRARY_PATH="/home/python/code/.venv/lib/"
RUN pip install /dist/*.whl
CMD ["python"]
