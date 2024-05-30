FROM python:3.12-slim

WORKDIR /code

RUN pip install kubernetes

COPY poetry.lock pyproject.toml ./

RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-root --without dev,test \
    && rm -rf $(poetry config cache-dir)/{cache,artifacts}

COPY ./app /code/app
WORKDIR /code

CMD ["python", "-m", "app.kg_exporter", "--incluster"]
