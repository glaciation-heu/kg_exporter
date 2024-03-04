# Kubernetes Watcher Service

The Kubernetes Watcher Service is a Python-based service that watches and detects changes for Kubernetes resources, such as Deployments, StatefulSets, and Jobs.

## Features

- Watches for changes to Kubernetes resources in real-time.
- Logs information about the changes detected.
- Supports monitoring of Deployments, StatefulSets, and Jobs.

## Usage
Deploy the service in a Kubernetes cluster using a Helm chart. After that, detected changes in the Kubernetes cluster will be displayed in the service logs.

## Development
### Prerequisites

- Python 3.11+
- Kubernetes cluster (local or remote)
- [Kubectl](https://kubernetes.io/docs/tasks/tools/)
- [Helm](https://helm.sh/docs/intro/install/)

### Installation and running
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

4. Running tests:
```bash
poetry run pytest
```

5. Launch the service:
```bash
poetry run python app/kg_exporter.py
```

## Manual building and deployment
1. Build and publish a docker image:
```bash
docker build . -t <image_name>:<image_tag>
docker login -u <username>
docker push <image_name>:<image_tag>
```
2. Configure `kubectl` to connect to the Kubernetes cluster.
3. Deploy the service to the Kubernetes cluster:
```bash
helm upgrade --install kg-exporter ./charts/app --set image.repository=<image_name> --set image.tag=<image_tag>
```

## Release
To create a release, add a tag in GIT with the format a.a.a, where 'a' is an integer.
The release version for branches, pull requests, and other tags will be generated based on the last tag of the form a.a.a.

## GitHub Actions
GitHub Actions triggers testing, builds, and application publishing for each release.  
https://docs.github.com/en/actions  

### Initial Setup
Create the branch gh-pages and use it as a GitHub page https://pages.github.com/.  
Set up secrets at `https://github.com/<workspace>/<project>/settings/secrets/actions`:

1. DOCKER_IMAGE_NAME - The name of the Docker image for uploading to the repository.
2. DOCKER_USERNAME - The username for the Docker repository on https://hub.docker.com/.
3. DOCKER_PASSWORD - The password for the Docker repository.
4. AWS_ACCESS_KEY_ID - AWS Secret Access Key ID.
   https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html
5. AWS_SECRET_ACCESS_KEY - AWS Secret Access Key
6. AWS_REGION - AWS region. https://aws.amazon.com/about-aws/global-infrastructure/regions_az/.
7. EKS_CLUSTER_ROLE_ARN - The IAM role's ARN in AWS, providing permissions for managing an AMAZON EKS
   Kubernetes Cluster.
8. EKS_CLUSTER_NAME - Amazon EKS Kubernetes cluster name.
9. EKS_CLUSTER_NAMESPACE - Amazon EKS Kubernetes cluster namespace.
10. HELM_REPO_URL - `https://<workspace>.github.io/<project>/`

**After execution**  
The index.yaml file containing the list of Helm charts will be available at `https://<workspace>.github.io/<project>/charts-repo/index.yaml`. You can this URL on https://artifacthub.io/.  
The service will be deployed in the Kubernetes cluster.

## Contributing
Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
