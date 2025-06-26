import asyncio
import logging
from sys import stdout

from boggart_2.app import Config, run_bot


def main():
    stream_handler = logging.StreamHandler(stream=stdout)
    date_format = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter(
        '[{asctime}] [{levelname}] {name}: {message}',
        date_format,
        style='{',
    )
    stream_handler.setFormatter(formatter)

    logger = logging.getLogger('boggart')
    logger.setLevel(logging.INFO)
    logger.addHandler(stream_handler)

    cfg = Config()
    asyncio.run(run_bot(cfg, logger))
