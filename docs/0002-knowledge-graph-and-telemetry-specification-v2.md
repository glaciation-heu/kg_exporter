# Knowledge Graph and Telemetry specification

# Amendments

| Date | Amendments |
| --- | --- |
| 13 may 2024 | - TradeOff Service API Response for Worker Node is adjusted<br/>- TradeOffService API Response for Workload is adjusted<br/>- Metric “Node energy consumption” for node is changed into “Node Energy Available” which is calculated as benchmarked node energy - consumed node energy.<br/>- Metric “Energy Used” for workload is added<br/>- Refined PromQL query examples for workload cpu usage |

# Worker Node

Terminology:

- Capacity - the maximum allocatable units of resource on the kubernetes worker node.
- Energy consumption: converting “<metric>_joules_total” (Counter) to milliwatts.

    Average using window of 5 minutes (300 seconds):

    - irate(kepler_node_platform_joules_total[300s]) / 300 = watts
    - irate(kepler_node_platform_joules_total[300s]) *1000 / 300 = milliwatts

| Metric | Source | Synthetic Data Generator | Knowledge graph, value of "glc:hasDescription" attribute of glc:Measurement | Tradeoff Service API Response, (JsonPath) |
| --- | --- | --- | --- | --- |
| Node energy index, milliwatt | Node resource:<br/>$.metadata.annotations.['glaciation-project.eu/metric/node-energy-index'] |  | node-energy-index | $.worker_nodes.resources.energy_index.max |
| Node CPU capacity max, cores | Node resource: <br/> $.status.allocatable.cpu | WN_CPU_MAX_CAPACITY | cpu-capacity-max | $.worker_nodes.resources.cpu.max |
| Node memory capacity max, Mb | Node resource: <br/> $.status.allocatable.memory | WN_MEM_MAX_CAPACITY | ram-capacity-max | $.worker_nodes.resources.memory.max |
| Node gpu capacity max, Flops | Not available yet | WN_GPU_MAX_CAPACITY | gpu-capacity-max | $.worker_nodes.resources.gpu.max |
| Node Storage capacity max (ephemeral storage), GB | TBD | WN_STR_MAX_CAPACITY | storage-capacity-max | $.worker_nodes.resources.storage.max |
| Node network capacity max, GB per second | Not available yet | WN_NET_MAX_CAPACITY | network-bandwidth-max | $.worker_nodes.resource.network.max |
| Node energy available, joules | Source: kepler<br/>node_energy_index - kepler_node_platform_joules_total{node=”glaciation-testm1w5-worker01”} | ENERGY_CONSUMPTION_MIN<br/> ENERGY_CONSUMPTION_MAX<br/>ENERGY_CONSUMPTION_MEDIAN<br/>ENERGY_CONSUMPTION_MEAN | node-energy-available | $.worker_nodes.resources.energy_index.available |
| Node CPU available, core seconds | Source: node exporter<br/>sum(rate(node_cpu_seconds_total{mode="idle", node="glaciation-testm1w5-worker01"}[5m])) | WN_CPU_AVAILABLE | cpu-capacity-available | $.worker_nodes.resources.cpu.available |
| Node Memory available, Mb | Source: node exporter<br/>node_memory_MemFree_bytes{instance="glaciation-testm1w5-worker01", app_kubernetes_io_component="metrics"} | WN_MEM_AVAILABLE  | ram-capacity-available | $.worker_nodes.resources.memory.available |
| Node GPU available, flops | Not available yet | WN_GPU_AVAILABLE | gpu-capacity-available | $.worker_nodes.resources.gpu.available |
| Node Storage available (PVC), Mb | Kubernetes metric:<br/>kubelet_volume_stats_available_bytes{instance="glaciation-testm1w5-worker01"}/ (1024 * 1024) | WN_STR_AVAILABLE | storage-capacity-available | $.worker_nodes.resources.storage.available |
| Network Storage available (ephemeral), Mb | cAdvisor metric:<br/>container_fs_usage_bytes{instance="glaciation-testm1w5-worker01"}/ (1024 * 1024) | WN_STR_AVAILABLE | storage-capacity-available | $.worker_nodes.resources.storage.available |
| Node Network available, Mb | TBD  | WN_NET_AVAILABLE | network-bandwidth-available | $.worker_nodes.resources.network.available |


# Workload

Terminology and interpretation:

- Used - how much resource units is consumed (usage in terms of kubernetes - cAdvisor source)
- Demanded - How much of resource units a user requests for a pod (”requests” in terms of kubernetes)
- Allocated - How much of a resources is maximally allowed for a pod (limits in terms of kubernetes, It can also be configured on the level of cluster. To be researched)

Example with a Counter and cpu usage:

- Instant query below returns the number of cores consumed by a pod for last sampling interval (~2 minutes):

```json
sum (
	rate(
		container_cpu_usage_seconds_total{pod="kube-flannel-ds-7wjqv"}[2m]
	)
)
```

- Total number of core-seconds consumed by a pod for a large window interval, e.g. 1 hour.

```json

sum (
	increase(
		container_cpu_usage_seconds_total{pod="kube-flannel-ds-7wjqv"}[1h]
	)
)

```

- Average number of core-seconds consumed by a pod during a large window interval, e.g. 1 hour.

```json

sum (
	rate(
		container_cpu_usage_seconds_total{pod="kube-flannel-ds-7wjqv"}[1h]
	)
)

```

| Metric description | Source (prometheus or k8s resource) | Synthetic Data Generator | Knowledge graph, value of "glc:hasDescription" attribute of glc:Measurement | Tradeoff Service |
| --- | --- | --- | --- | --- |
| Network received usage, Mb | cAdvisor:<br/>sum(rate(container_network_receive_bytes_total[2m])) by (pod) / (1024 * 1024) | WL_NET_REC_USG_AVG<br/>WL_NET_REC_USG_MED<br/>WL_NET_REC_USG_MAX<br/>WL_NET_REC_USG_MIN | network-received | $.workloads.resources.network.used |
| Network transfer usage, Mbit per second | cAdvisor:<br/>sum(rate(container_network_transmit_bytes_total[2m])) by (pod) | WL_NET_TRN_USG_MIN<br/>WL_NET_TRN_USG_MAX<br/>WL_NET_TRN_USG_MED<br/>WL_NET_TRN_USG_AVG | network-transferred | $.workloads.resources.network.used |
| Storage read usage, Mb per second | cAdvisor:<br/>sum(rate(container_fs_reads_bytes_total[2m])) by (pod,device) / (1024 * 1024) | WL_STR_RED_USG_AVG<br/>WL_STR_RED_USG_MAX<br/>WL_STR_RED_USG_MIN<br/>WL_STR_RED_USG_MED | storage-read | $.workloads.resources.storage.used |
| Storage write usage, MB per second | cAdvisor:<br/>sum(rate(container_fs_writes_bytes_total[2m])) by (pod,device) | WL_STR_WRT_USG_MIN<br/>WL_STR_WRT_USG_MAX<br/>WL_STR_WRT_USG_MED<br/>WL_STR_WRT_USG_AVG | storage-write | $.workloads.resources.storage.used |
| Cpu usage minimum, unit: cores seconds | cAdvisor:<br/>sum(rate(container_cpu_usage_seconds_total[2m])) by (pod) | WL_CPU_USG_MIN<br/>WL_CPU_USG_MAX<br/>WL_CPU_USG_MED<br/>WL_CPU_USG_AVG | cpu-used | $.workloads.resources.cpu.used |
| Memory usage, Mb (and can be fractional) | cAdvisor:<br/>sum(container_memory_working_set_bytes) by (pod) /(1024*1024) | WL_MEM_USG_MIN<br/>WL_MEM_USG_MAX<br/>WL_MEM_USG_MED<br/>WL_MEM_USG_AVG | ram-used | $.workloads.resources.memory.used |
| GPU usage, flops | Not available, device specific k8s plugin | WL_GPU_USG_MIN<br/>WL_GPU_USG_MAX<br/>WL_GPU_USG_MED<br/>WL_GPU_USG_AVG | gpu-used | $.workloads.resources.gpu.used |
| Energy Used, milliwatt | Kepler<br/>sum (kepler_container_joules_total[2m]) by (pod_name) | ENERGY_CONSUMPTION_MIN<br/>ENERGY_CONSUMPTION_MAX<br/>ENERGY_CONSUMPTION_MED<br/>ENERGY_CONSUMPTION_AVG | energy-used | $.workloads.resources.energy_index.used |
| CPU limit, cores | K8s Deployment Resource<br/>$.spec.containers[].resources.limits.cpu | WL_CPU_ALC | cpu-limits | $.workloads.resources.cpu.allocated |
| GPU limit, flops | K8s Deployment Resource<br/>$.spec.metadata.annotations[name=”glaciation-project.eu/resource/limits/gpu”] | WL_GPU_ALC | gpu-limits | $.workloads.resources.gpu.allocated |
| Network limit, megabyte | K8s Deployment Resource<br/>$.spec.metadata.annotations[name=”glaciation-project.eu/resource/limits/network”] | WL_NET_ALC | network-limits | $.workloads.resources.network.allocated |
| Storage limit, gigabyte | K8s Deployment Resource<br/>$.spec.containers[].resources.limits.ephemeral-storage | WL_STR_ALC | storage-limits | $.workloads.resources.storage.allocated |
| Memory limit, megabytes | K8s Deployment Resource<br/>$.spec.containers[name=”container-name”].resources.limits.memory | WL_MEM_ALC | memory-limits | $.workloads.resources.memory.allocated |
| Energy limit, milliwatt | K8s Deployment Resource<br/>$.spec.metadata.annotations[name=”glaciation-project.eu/resource/limits/energy”] | WL_ENERGY_ALC | energy-limits | $.workloads.resources.energy_index.allocated |
| CPU requests, cores | K8s Deployment Resource<br/>$.spec.containers[].resources.requests.cpu | WL_CPU_DEM | cpu-requests | $.workloads.resources.cpu.demanded |
| Memory requests, Mb | K8s Deployment Resource<br/>$.spec.containers[name=”container-name”].resources.requests.memory | WL_MEM_DEM | ram-requests | $.workloads.resources.memory.demanded |
| GPU requests, flops | K8s Deployment Resource<br/>$.spec.metadata.annotations[name=”glaciation-project.eu/resource/requests/gpu”] | WL_GPU_DEM | gpu-requests | $.workloads.resources.gpu.demanded |
| Storage requests, GB | K8s Deployment Resource<br/>$.spec.containers[].resources.requests.ephemeral-storage | WL_STR_DEM | storage-requests | $.workloads.resources.storage.demanded |
| Network requests, Mb | K8s Deployment Resource<br/>$.spec.metadata.annotations[name=”glaciation-project.eu/resource/requests/network”] | WL_NET_DEM | network-requests | $.workloads.resources.network.demanded |
| Energy requests, milliwatts | K8s Deployment Resource<br/>$.spec.metadata.annotations[name=”glaciation-project.eu/resource/requests/energy”] | WL_ENERGY_DEM | energy-requests | $.workloads.resources.energy_index.demanded |

# Sample K8S resources, Knowledge graphs and TradeOffService API

 - Worker Node
    - [K8s worker node](./0002-knowledge-graph-and-telemetry-specification-v2/workernode-k8s-node.yaml)
    - [Worker node metadata graph](./0002-knowledge-graph-and-telemetry-specification-v2/workernode-metadata-graph.jsonld)
    - [TradeOffService Node API](./0002-knowledge-graph-and-telemetry-specification-v2/workernode-tradeoff-service-api.json)

- Workload
    - [K8s Workload](./0002-knowledge-graph-and-telemetry-specification-v2/workload-k8s-deployment.yaml) (Deployment/ReplicaSet/Pod)
    - [Workload metadata graph](./0002-knowledge-graph-and-telemetry-specification-v2/workload-metadata-graph.jsonld)
    - [TradeOffService Workload API](./0002-knowledge-graph-and-telemetry-specification-v2/workload-tradeoff-service-api.json)

## References:

1. cAdvisor metrics [https://github.com/google/cadvisor/blob/master/docs/storage/prometheus.md](https://github.com/google/cadvisor/blob/master/docs/storage/prometheus.md)
2. Kubernetes metrics [https://kubernetes.io/docs/reference/instrumentation/metrics/](https://kubernetes.io/docs/reference/instrumentation/metrics/)

3. Allocatable Memory in kubernetes: [https://dev.to/ridaehamdani/understanding-allocatable-memory-and-cpu-in-kubernetes-nodes-4hbm#:~:text=In Kubernetes%2C allocatable resources refer,available CPU and memory resources](https://dev.to/ridaehamdani/understanding-allocatable-memory-and-cpu-in-kubernetes-nodes-4hbm#:~:text=In%20Kubernetes%2C%20allocatable%20resources%20refer,available%20CPU%20and%20memory%20resources)

4. Prometheus metrics parsing [https://docs.influxdata.com/influxdb/v1/supported_protocols/prometheus/](https://docs.influxdata.com/influxdb/v1/supported_protocols/prometheus/)
