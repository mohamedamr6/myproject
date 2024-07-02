# Use the official Python image as a base
FROM python:3.9

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY pyproject.toml poetry.lock /app/

# Install Poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -

# Install dependencies using Poetry
RUN $HOME/.poetry/bin/poetry config virtualenvs.create false && $HOME/.poetry/bin/poetry install --no-interaction --no-ansi

# Copy the current directory contents into the container at /app
COPY . /app/

# Run collectstatic
RUN $HOME/.poetry/bin/poetry run python manage.py collectstatic --no-input

# Expose the port django is running on
EXPOSE 8000

# Run the Django development server
CMD ["$HOME/.poetry/bin/poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]