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