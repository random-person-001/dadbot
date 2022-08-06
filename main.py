import logging
import os

import discord
import toml

from mybot import MyBot


def setup_logging():
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename='logs/discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)


def prep():
    """Make sure the environment and config stuff is set up right, giving hopefully helpful messages if not"""
    if discord.__version__[0] == '1':  # async is about 0.16, rewrite is 1.0+
        print("Looks like you're using the older discord.py library. This is written in v2. "
              "You should really run this with pipenv instead of on your system environment... see the readme.md")
        return
    try:
        config = toml.load("config.toml")
    except (TypeError, toml.TomlDecodeError):
        print("Oy, it looks like your `config.toml` file is incorrectly formatted")
        return
    except FileNotFoundError:
        print("Oops, couldn't find a config file. Try renaming `exampleconfig.toml` to `config.toml` "
              "(more help can be found in the file `readme.md`)")
        return
    else:
        if not os.path.exists('logs'):  # make sure we have a place to log errors if we encounter them
            os.mkdir('logs')
        for key in ('token', 'prefix', "extensions"):
            if key not in config:
                print('Oof, looks like you\'re missing the entry for `{}` in the config.toml file. '
                      'Perhaps reference `exampleconfig.toml`?'.format(key))
                return
        return config


if __name__ == '__main__':
    config = prep()
    setup_logging()
    if config:
        MyBot(config).startup()
