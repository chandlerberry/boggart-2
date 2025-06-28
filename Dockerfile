FROM ghcr.io/astral-sh/uv:alpine3.21

ADD . /app

WORKDIR /app
RUN uv sync --locked --compile-bytecode

ENV BOGGART_CONFIG_PATH=/config.yml

CMD ["uv", "run", "boggart"]
