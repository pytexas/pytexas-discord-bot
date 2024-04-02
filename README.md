# pytexas-discord-bot
Discord bot for the PyTexas Discord

Use pip to install, e.g.:

    pip install -e .

or

    pip install -e .[dev]

to install dev tools as well.

Requires following env vars:

    - DISCORD_TOKEN
    - DISCORD_GUILD
    - PRETIX_API_TOKEN

These can be loaded from the shell environment or from a .env file.

Note that if you don't use a .env file, you will need to use a different run
command than is in the Makefile.


Docker notes:

    - use included Dockerfile to build image:
      docker build -t <image_name> .
    - to run: docker run -it --env-file ./.env <image_name>
    - you will need to generate a requirements.txt file in order for the docker
      build to succeed
