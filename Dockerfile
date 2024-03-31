# Initial image
# Note: bookworm breaks for some reason, maybe incompatibility with it's
#       seccomp setup and certain versions of docker?
#       So we use bullseye instead.
# FROM python:3.11-slim-bookworm
FROM python:3.11-slim-bullseye

# Set local username
ENV USERNAME=appuser

# Set up non-root user and work directory
RUN useradd --create-home "$USERNAME"
WORKDIR /home/"$USERNAME"
USER "$USERNAME"

# Create and activate virtualenv
ENV VIRTUAL_ENV=/home/"$USERNAME"/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# upgrade pip in virtualenv
RUN python -m pip install --upgrade pip

# Install requirements
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

# Copy application files
COPY --chown="$USERNAME":"$USERNAME" . ./app

# Install application
RUN pip install --no-deps ./app

# Start application
CMD ["python", "-m", "pytexbot"]
