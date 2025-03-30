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

If you use a .env file, it is recommended to place it in the /src directory.

The PRETIX_API_TOKEN must be created on a team that has access to the relevant
event.  Check the team settings in Pretix and make sure the box next to the
relevant event is checked.


Docker notes:

    - use included Dockerfile to build image:
      docker build -t <image_name> .
    - to run attached to terminal: docker run -it --env-file ./.env <image_name>
    - to run detached: docker run -d --env-file ./.env <image_name>
    - you will need to generate a requirements.txt file in order for the docker
      build to succeed

Note that there is a Makefile which automates most of these docker operations.

TODO: document how to set up discord permissions for a new discord token
