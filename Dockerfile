FROM astral/uv:python3.13-trixie

COPY . .

RUN uv sync --locked --compile-bytecode

ENV BOGGART_CONFIG_PATH="/config.yml"

CMD ["uv", "run", "boggart"]
