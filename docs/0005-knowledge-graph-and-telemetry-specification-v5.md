# Knowledge Graph and Telemetry specification


# Amendments

| Date | Amendments |
| --- | --- |
| 13 may 2024 | - TradeOff Service API Response for Worker Node is adjusted<br/>- TradeOffService API Response for Workload is adjusted<br/>- Metric “Node energy consumption” for node is changed into “Node Energy Available” which is calculated as benchmarked node energy - consumed node energy.<br/>- Metric “Energy Used” for workload is added<br/>- Refined PromQL query examples for workload cpu usage |
| 17 Jul 2024 | - Knowledge graph measurement “descriptions” are aligned and unified<br/>- GPU resource constraints and allocations are set by GPU plugin |
| 27 Aug 2024 | - Prometheus queries are updated |
|  8 Apr 2025 | - Corrected specification for energy and network capacity/allocated metrics |

# Worker Node

Terminology:

- Capacity - the maximum allocatable units of resource on the kubernetes worker node.
- Energy consumption: converting "<metric>_joules_total" (Counter) to milliwatts.

    Average using window of 5 minutes (300 seconds):

    - irate(kepler_node_platform_joules_total[300s]) / 300 = watts
    - irate(kepler_node_platform_joules_total[300s]) * 1000 / 300 = milliwatts

| Metric | Source | Synthetic Data Generator | Knowledge graph, value of "glc:hasDescription" attribute of glc:Measurement | Tradeoff Service API Response, (JsonPath) |
| --- | --- | --- | --- | --- |
| Node energy index, milliwatt | Node resource:<br/> $.metadata.annotations.['glaciation-project.eu/node-energy-index'] |  | Energy.Index | $.worker_nodes.resources.energy_index.max |
| Node CPU capacity max, cores | Node resource: <br/>$.status.allocatable.cpu | WN_CPU_MAX_CAPACITY | CPU.Capacity | $.worker_nodes.resources.cpu.max |
| Node memory capacity max, Mb | Node resource: <br/>$.status.allocatable.memory | WN_MEM_MAX_CAPACITY | RAM.Capacity | $.worker_nodes.resources.memory.max |
| Node gpu capacity max, unit | Node resource: <br/>$.status.capacity.”nvidia.com/gpu” | WN_GPU_MAX_CAPACITY | GPU.Capacity | $.worker_nodes.resources.gpu.max |
| Node Storage capacity max, bytes | Node resource: <br/>$.status.allocatable.ephemeral-storage | WN_STR_MAX_CAPACITY | Storage.Capacity | $.worker_nodes.resources.storage.max |
| Node Network capacity max, bytes | Not available | WN_NET_MAX_CAPACITY | Network.Capacity | $.worker_nodes.resource.network.max |
| Node Energy usage, joules | Source: kepler <br/>irate(kepler_node_platform_joules_total[5m]) |ENERGY_CONSUMPTION_MIN<br/>ENERGY_CONSUMPTION_MAX<br/>ENERGY_CONSUMPTION_MEDIAN<br/>ENERGY_CONSUMPTION_MEAN | Energy.Usage | $.worker_nodes.resources.energy_index.available |
| Node CPU available, core seconds | Source: node exporter <br/> sum(rate(node_cpu_seconds_total{mode="idle", service="monitoring-stack-prometheus-node-exporter"}[5m])) by (node) | WN_CPU_AVAILABLE | CPU.Available | $.worker_nodes.resources.cpu.available |
| Node Memory available, Mb | Source: node exporter <br/>node_memory_MemFree_bytes{service="monitoring-stack-prometheus-node-exporter"} | WN_MEM_AVAILABLE  | RAM.Available | $.worker_nodes.resources.memory.available |
| Node GPU available, unit | Node resource: <br/>$.status.allocatable.”nvidia.com/gpu” | WN_GPU_AVAILABLE | GPU.Available | $.worker_nodes.resources.gpu.available |
| Node Storage available (ephemeral), bytes | k8s ephemeral metrics: <br/>ephemeral_storage_node_available | WN_STR_AVAILABLE | Storage.Available | $.worker_nodes.resources.storage.available |
| Node Network available, bytes | Not Available  | WN_NET_AVAILABLE | Network.Available | $.worker_nodes.resources.network.available |

# Workload

Terminology and interpretation:

- Used - how much resource units is consumed (usage in terms of kubernetes - cAdvisor source)
- Allocated - How much of resource units a user requests for a pod (”requests” in terms of kubernetes)
- Capacity - How much of a resources is maximally allowed for a pod (limits in terms of kubernetes, It can also be configured on the level of cluster. To be researched)

Example with a Counter and cpu usage:

- Instant query below returns the number of cores consumed by a pod for last sampling interval (~2 minutes):

```promql
sum (
	rate(
		container_cpu_usage_seconds_total{pod="kube-flannel-ds-7wjqv"}[2m]
	)
)
```

- Total number of core-seconds consumed by a pod for a large window interval, e.g. 1 hour.

```promql

sum (
	increase(
		container_cpu_usage_seconds_total{pod="kube-flannel-ds-7wjqv"}[1h]
	)
)

```

- Average number of core-seconds consumed by a pod during a large window interval, e.g. 1 hour.

```promql

sum (
	rate(
		container_cpu_usage_seconds_total{pod="kube-flannel-ds-7wjqv"}[1h]
	)
)

```

| Metric description | Source (prometheus or k8s resource) | Synthetic Data Generator | Knowledge graph, value of "glc:hasDescription" attribute of glc:Measurement | Tradeoff Service |
| --- | --- | --- | --- | --- |
| Network usage (sent+received), bytes | cAdvisor: <br/>sum(rate(container_network_receive_bytes_total[5m])) by (namespace, pod) + <br/>sum(rate(container_network_transmit_bytes_total[5m])) by (namespace, pod) | WL_NET_REC_USG_AVG <br/>WL_NET_REC_USG_MED<br/>WL_NET_REC_USG_MAX<br/>WL_NET_REC_USG_MIN | Network.Usage | $.workloads.resources.network.used |
| Storage (ephemeral), bytes | cAdvisor:<br/>ephemeral_storage_pod_usage | WL_STR_RED_USG_AVG<br/>WL_STR_RED_USG_MAX<br/>WL_STR_RED_USG_MIN<br/>WL_STR_RED_USG_MED | Storage.Usage | $.workloads.resources.storage.used |
| Cpu usage minimum, unit: cores seconds | cAdvisor:<br/>sum(rate(container_cpu_usage_seconds_total[5m])) by (namespace, pod) | WL_CPU_USG_MIN<br/>WL_CPU_USG_MAX<br/>WL_CPU_USG_MED<br/>WL_CPU_USG_AVG | CPU.Usage | $.workloads.resources.cpu.used |
| Memory usage, bytes | cAdvisor:<br/>sum(rate(container_memory_working_set_bytes[5m])) by (namespace, pod) | WL_MEM_USG_MIN<br/>WL_MEM_USG_MAX<br/>WL_MEM_USG_MED<br/>WL_MEM_USG_AVG | RAM.Usage | $.workloads.resources.memory.used |
| GPU usage, % | dcgm-exporter:<br/>DCGM_FI_DEV_GPU_UTIL | WL_GPU_USG_MIN<br/>WL_GPU_USG_MAX<br/>WL_GPU_USG_MED<br/>WL_GPU_USG_AVG | GPU.Usage | $.workloads.resources.gpu.used |
| Energy Used, milliwatt | Kepler<br/>sum(irate(kepler_container_joules_total[5m])) by (container_namespace, pod_name) | ENERGY_CONSUMPTION_MIN<br/>ENERGY_CONSUMPTION_MAX<br/>ENERGY_CONSUMPTION_MED<br/>ENERGY_CONSUMPTION_AVG | Energy.Usage | $.workloads.resources.energy_index.used |
| CPU limit, cores | K8s Deployment Resource<br/>$.spec.containers[].resources.limits.cpu | WL_CPU_ALC | CPU.Capacity | $.workloads.resources.cpu.allocated |
| GPU limit, unit | K8s Deployment Resource<br/>$.spec.containers[].resources.limits.”nvidia.com/gpu” | WL_GPU_ALC | GPU.Capacity | $.workloads.resources.gpu.allocated |
| Network limit, megabyte | K8s Deployment Resource<br/>$.spec.metadata.annotations[name=”glaciation-project.eu/network-capacity”] | WL_NET_ALC | Network.Capacity | $.workloads.resources.network.allocated |
| Storage limit, gigabyte | K8s Deployment Resource<br/>$.spec.containers[].resources.limits.ephemeral-storage | WL_STR_ALC | Storage.Capacity | $.workloads.resources.storage.allocated |
| Memory limit, megabytes | K8s Deployment Resource<br/>$.spec.containers[name=”container-name”].resources.limits.memory | WL_MEM_ALC | RAM.Capacity | $.workloads.resources.memory.allocated |
| Energy limit, milliwatt | K8s Deployment Resource<br/>$.spec.metadata.annotations[name=”glaciation-project.eu/energy-capacity”] | WL_ENERGY_ALC | Energy.Capacity | $.workloads.resources.energy_index.allocated |
| CPU requests, cores | K8s Deployment Resource<br/>$.spec.containers[].resources.requests.cpu | WL_CPU_DEM | CPU.Allocated | $.workloads.resources.cpu.demanded |
| Memory requests, Mb | K8s Deployment Resource<br/>$.spec.containers[name=”container-name”].resources.requests.memory | WL_MEM_DEM | RAM.Allocated | $.workloads.resources.memory.demanded |
| GPU requests, unit | K8s Deployment Resource<br/>$.spec.containers[].resources.requests.”nvidia.com/gpu” | WL_GPU_DEM | GPU.Allocated | $.workloads.resources.gpu.demanded |
| Storage requests, GB | K8s Deployment Resource<br/>$.spec.containers[].resources.requests.ephemeral-storage | WL_STR_DEM | GPU.Allocated | $.workloads.resources.storage.demanded |
| Network requests, Mb | K8s Deployment Resource<br/>$.spec.metadata.annotations[name=”glaciation-project.eu/network-allocated”] | WL_NET_DEM | Network.Allocated | $.workloads.resources.network.demanded |
| Energy requests, milliwatts | K8s Deployment Resource<br/>$.spec.metadata.annotations[name=”glaciation-project.eu/energy-allocated”] | WL_ENERGY_DEM | Energy.Allocated | $.workloads.resources.energy_index.demanded |


# Sample K8S resources, Knowledge graphs and TradeOffService API

 - Worker Node
    - [K8s worker node](./0005-knowledge-graph-and-telemetry-specification-v5/workernode-k8s-node.yaml)
    - [Worker node metadata graph](./0005-knowledge-graph-and-telemetry-specification-v5/workernode-metadata-graph.jsonld)
    - [TradeOffService Node API](./0005-knowledge-graph-and-telemetry-specification-v5/workernode-tradeoff-service-api.json)

- Workload
    - [K8s Workload](./0005-knowledge-graph-and-telemetry-specification-v5/workload-k8s-deployment.yaml) (Deployment/ReplicaSet/Pod)
    - [Workload metadata graph](./0005-knowledge-graph-and-telemetry-specification-v5/workload-metadata-graph.jsonld)
    - [TradeOffService Workload API](./0005-knowledge-graph-and-telemetry-specification-v5/workload-tradeoff-service-api.json)

## References:

1. cAdvisor metrics [https://github.com/google/cadvisor/blob/master/docs/storage/prometheus.md](https://github.com/google/cadvisor/blob/master/docs/storage/prometheus.md)

2. Kubernetes metrics [https://kubernetes.io/docs/reference/instrumentation/metrics/](https://kubernetes.io/docs/reference/instrumentation/metrics/)

3. Allocatable Memory in kubernetes: [https://dev.to/ridaehamdani/understanding-allocatable-memory-and-cpu-in-kubernetes-nodes-4hbm#:~:text=In Kubernetes%2C allocatable resources refer,available CPU and memory resources](https://dev.to/ridaehamdani/understanding-allocatable-memory-and-cpu-in-kubernetes-nodes-4hbm#:~:text=In%20Kubernetes%2C%20allocatable%20resources%20refer,available%20CPU%20and%20memory%20resources)

4. Prometheus metrics parsing [https://docs.influxdata.com/influxdb/v1/supported_protocols/prometheus/](https://docs.influxdata.com/influxdb/v1/supported_protocols/prometheus/)

5. NVIDIA k8s-device-plugin [https://github.com/NVIDIA/k8s-device-plugin](https://github.com/NVIDIA/k8s-device-plugin)

6. GPU Metrics Exporter [https://github.com/NVIDIA/dcgm-exporter](https://github.com/NVIDIA/dcgm-exporter)
