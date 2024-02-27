# Kubernetes Watcher Service

The Kubernetes Watcher Service is a Python-based service that watches and detects changes for Kubernetes resources, such as Deployments, StatefulSets, and Jobs. It is designed to generate a knowledge graph for these resources and push it to a metadata service.

## Features

Watches for changes to Kubernetes resources in real-time.

Logs information about the changes detected.

Supports monitoring of Deployments, StatefulSets, and Jobs.

Integrates with Helm for easy deployment and management.



## Getting Started
### Prerequisites

Python 3.x

Kubernetes cluster (local or remote)

Helm (for Helm chart integration)

### Installation
<details>
<summary>Install Python 3.12 if it is not available in your package manager</summary>

These instructions are for Ubuntu 22.04. If you're on a different distribution,
or - God forbid! - Windows, you should adjust these accordingly.

Also, these instructions are about using Poetry with Pyenv-managed (non-system) Python.
 
### Step 1: Update and Install Dependencies
Before we install pyenv, we need to update our package lists for upgrades and new package installations. We also need to install dependencies for pyenv. 

Open your terminal and type:
```bash
sudo apt-get update
sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev \
libreadline-dev libsqlite3-dev wget curl llvm libncursesw5-dev xz-utils \
tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
```

### Step 2: Install Pyenv
We will clone pyenv from the official GitHub repository and add it to our system path.
```bash
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
exec "$SHELL"
```

### Step 3: Install Python 3.12
Now that pyenv is installed, we can install different Python versions. To install Python 3.12, use the following command:
```bash
pyenv install 3.12
```

### Step 4: Connect Poetry to it
Do this in the template dir. Pycharm will automatically connect to it later
```bash
poetry env use ~/.pyenv/versions/3.12.1/bin/python
```
(change the version number accordingly to what is installed)

Finally, verify that Poetry indeed is connected to the proper version:
```bash
poetry enf info
```
</details>  

1. If you don't have `Poetry` installed run:
```bash
pip install poetry
```

2. Install dependencies:
```bash
poetry config virtualenvs.in-project true
poetry install --no-root --with dev,test
```

3. Install `pre-commit` hooks:
```bash
poetry run pre-commit install
```

4. Launch the project:
```bash
poetry run uvicorn app.main:app [--reload]
```
or do it in two steps:
```bash
poetry shell
uvicorn app.main:app
```

5. Running tests:
```bash
poetry run pytest
```

You can test the application for multiple versions of Python. To do this, you need to install the required Python versions on your operating system, specify these versions in the tox.ini file, and then run the tests:
```bash
poetry run tox
```

## Package
To generate and publish a package on pypi.org, execute the following commands:
```bash
poetry config pypi-token.pypi <pypi_token>
poetry build
poetry publish
```

pypi_token - API token for authentication on PyPI. https://pypi.org/help/#apitoken

## Docker
Build a docker image and run a container:
```bash
docker build . -t <image_name>:<image_tag>
docker run <image_name>:<image_tag>
```

Upload the Docker image to the repository:
```bash
docker login -u <username>
docker push <image_name>:<image_tag>
```

https://docs.docker.com/

## Helm chart
Authenticate your Helm client in the container registry:
```bash
helm registry login <repo_url> -u <username>
```

Create a Helm chart:
```bash
helm package charts/<chart_name>
```

Push the Helm chart to container registry:
```bash
helm push <helm_chart_package> <repo_url>
```

Deploy the Helm chart:
```bash
helm repo add <repo_name> <repo_url>
helm repo update <repo_name>
helm upgrade --install <release_name> <repo_name>/<chart_name>
```

https://helm.sh/ru/docs/

## OpenaAPI schema
To manually generate the OpenAPI schema, execute the command:
```bash
poetry run python ./tools/extract_openapi.py app.main:app --app-dir . --out openapi.yaml --app_version <version>
```

## Release
To create a release, add a tag in GIT with the format a.a.a, where 'a' is an integer.
The release version for branches, pull requests, and other tags will be generated based on the last tag of the form a.a.a.

## GitHub Actions
GitHub Actions triggers testing, builds, and application publishing for each release.  
https://docs.github.com/en/actions  

You can set up automatic testing in GitHub Actions for different versions of Python. To do this, you need to specify the set of versions in the .github/workflows/test_and_build.yaml file. For example:
```yaml
strategy:
  matrix:
    python-version: ["3.10", "3.11", "3.12"]
```

The process of building and publishing differs for web services and libraries.

Clone this repository:
```bash
git clone https://github.com/your-username/kubernetes-watcher.git
```

### Usage
Initialize Kubernetes configuration:
```bash
kubectl config use-context <context-name>
```
Run the watcher service:
```bash
python kg_exporter.py
```
### Helm Chart Deployment
Navigate to the helm-chart directory:
```bash
cd app/templates
```
Customize the chart values in values.yaml as needed.

Deploy the Helm chart:
```bash
helm install kg-exporter ./kg-exporter-chart
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)