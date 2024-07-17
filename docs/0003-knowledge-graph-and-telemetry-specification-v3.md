# Knowledge Graph and Telemetry specification


# Amendments

| Date | Amendments |
| --- | --- |
| 13 may 2024 | - TradeOff Service API Response for Worker Node is adjusted<br/>- TradeOffService API Response for Workload is adjusted<br/>- Metric “Node energy consumption” for node is changed into “Node Energy Available” which is calculated as benchmarked node energy - consumed node energy.<br/>- Metric “Energy Used” for workload is added<br/>- Refined PromQL query examples for workload cpu usage |
| 17 Jul 2024 | - Knowledge graph measurement “descriptions” are aligned and unified<br/>- GPU resource constraints and allocations are set by GPU plugin |

# Worker Node

Terminology:

- Capacity - the maximum allocatable units of resource on the kubernetes worker node.
- Energy consumption: converting "<metric>_joules_total" (Counter) to milliwatts.

    Average using window of 5 minutes (300 seconds):

    - irate(kepler_node_platform_joules_total[300s]) / 300 = watts
    - irate(kepler_node_platform_joules_total[300s]) *1000 / 300 = milliwatts

| Metric | Source | Synthetic Data Generator | Knowledge graph, value of "glc:hasDescription" attribute of glc:Measurement | Tradeoff Service API Response, (JsonPath) |
| --- | --- | --- | --- | --- |
| Node energy index, milliwatt | Node resource:<br/> $.metadata.annotations.['glaciation-project.eu/metric/node-energy-index'] |  | Energy.Index | $.worker_nodes.resources.energy_index.max |
| Node CPU capacity max, cores | Node resource: <br/>$.status.allocatable.cpu | WN_CPU_MAX_CAPACITY | CPU.Capacity | $.worker_nodes.resources.cpu.max |
| Node memory capacity max, Mb | Node resource: <br/>$.status.allocatable.memory | WN_MEM_MAX_CAPACITY | RAM.Capacity | $.worker_nodes.resources.memory.max |
| Node gpu capacity max, unit | Node resource: <br/>$.status.capacity.”nvidia.com/gpu” | WN_GPU_MAX_CAPACITY | GPU.Capacity | $.worker_nodes.resources.gpu.max |
| Node Storage capacity max (ephemeral storage), GB | TBD, (ephemeral storage helm chart) | WN_STR_MAX_CAPACITY | Storage.Capacity | $.worker_nodes.resources.storage.max |
| Node network capacity max, GB per second | Not available yet | WN_NET_MAX_CAPACITY | Network.Capacity | $.worker_nodes.resource.network.max |
| Node energy available, joules | Source: kepler <br/>node_energy_index - kepler_node_platform_joules_total{node=”glaciation-testm1w5-worker01”} |ENERGY_CONSUMPTION_MIN<br/>ENERGY_CONSUMPTION_MAX<br/>ENERGY_CONSUMPTION_MEDIAN<br/>ENERGY_CONSUMPTION_MEAN | Energy.Available | $.worker_nodes.resources.energy_index.available |
| Node CPU available, core seconds | Source: node exporter <br/> sum(rate(node_cpu_seconds_total{mode="idle", node="glaciation-testm1w5-worker01"}[5m])) | WN_CPU_AVAILABLE | CPU.Available | $.worker_nodes.resources.cpu.available |
| Node Memory available, Mb | Source: node exporter <br/>node_memory_MemFree_bytes{instance="glaciation-testm1w5-worker01", app_kubernetes_io_component="metrics"} | WN_MEM_AVAILABLE  | RAM.Available | $.worker_nodes.resources.memory.available |
| Node GPU available, unit | Node resource: <br/>$.status.allocatable.”nvidia.com/gpu” | WN_GPU_AVAILABLE | GPU.Available | $.worker_nodes.resources.gpu.available |
| Node Storage available (PVC), Mb | Kubernetes metric: <br/>kubelet_volume_stats_available_bytes{instance="glaciation-testm1w5-worker01"}/ (1024 * 1024) | WN_STR_AVAILABLE | Storage.Available | $.worker_nodes.resources.storage.available |
| Network Storage available (ephemeral), Mb | cAdvisor metric: <br/>container_fs_usage_bytes{instance="glaciation-testm1w5-worker01"}/ (1024 * 1024) | WN_STR_AVAILABLE | Storage.Available | $.worker_nodes.resources.storage.available |
| Node Network available, Mb | TBD  | WN_NET_AVAILABLE | Network.Available | $.worker_nodes.resources.network.available |

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
| Network received usage, Mb | cAdvisor: <br/>sum(rate(container_network_receive_bytes_total[2m])) by (pod) / (1024 * 1024) | WL_NET_REC_USG_AVG <br/>WL_NET_REC_USG_MED<br/>WL_NET_REC_USG_MAX<br/>WL_NET_REC_USG_MIN | Network.Usage | $.workloads.resources.network.used |
| Network transfer usage, Mbit per second | cAdvisor: <br/>sum(rate(container_network_transmit_bytes_total[2m])) by (pod) | WL_NET_TRN_USG_MIN <br/>WL_NET_TRN_USG_MAX<br/>WL_NET_TRN_USG_MED <br/>WL_NET_TRN_USG_AVG | Network.Usage | $.workloads.resources.network.used |
| Storage read usage, Mb per second | cAdvisor:<br/>sum(rate(container_fs_reads_bytes_total[2m])) by (pod,device) / (1024 * 1024) | WL_STR_RED_USG_AVG<br/>WL_STR_RED_USG_MAX<br/>WL_STR_RED_USG_MIN<br/>WL_STR_RED_USG_MED | Storage.Usage | $.workloads.resources.storage.used |
| Storage write usage, MB per second |cAdvisor:<br/>sum(rate(container_fs_writes_bytes_total[2m])) by (pod,device) |WL_STR_WRT_USG_MIN<br/>WL_STR_WRT_USG_MAX<br/>WL_STR_WRT_USG_MED<br/>WL_STR_WRT_USG_AVG | Storage.Usage | $.workloads.resources.storage.used |
| Cpu usage minimum, unit: cores seconds | cAdvisor:<br/>sum(rate(container_cpu_usage_seconds_total[2m])) by (pod) | WL_CPU_USG_MIN<br/>WL_CPU_USG_MAX<br/>WL_CPU_USG_MED<br/>WL_CPU_USG_AVG | CPU.Usage | $.workloads.resources.cpu.used |
| Memory usage, Mb (and can be fractional) | cAdvisor:<br/>sum(container_memory_working_set_bytes) by (pod) /(1024*1024) | WL_MEM_USG_MIN<br/>WL_MEM_USG_MAX<br/>WL_MEM_USG_MED<br/>WL_MEM_USG_AVG | RAM.Usage | $.workloads.resources.memory.used |
| GPU usage, % | dcgm-exporter:<br/>DCGM_FI_DEV_GPU_UTIL | WL_GPU_USG_MIN<br/>WL_GPU_USG_MAX<br/>WL_GPU_USG_MED<br/>WL_GPU_USG_AVG | GPU.Usage | $.workloads.resources.gpu.used |
| Energy Used, milliwatt | Kepler<br/>sum (kepler_container_joules_total[2m]) by (pod_name) | ENERGY_CONSUMPTION_MIN<br/>ENERGY_CONSUMPTION_MAX<br/>ENERGY_CONSUMPTION_MED<br/>ENERGY_CONSUMPTION_AVG | Energy.Usage | $.workloads.resources.energy_index.used |
| CPU limit, cores | K8s Deployment Resource<br/>$.spec.containers[].resources.limits.cpu | WL_CPU_ALC | CPU.Capacity | $.workloads.resources.cpu.allocated |
| GPU limit, unit | K8s Deployment Resource<br/>$.spec.containers[].resources.limits.”nvidia.com/gpu” | WL_GPU_ALC | GPU.Capacity | $.workloads.resources.gpu.allocated |
| Network limit, megabyte | K8s Deployment Resource<br/>$.spec.metadata.annotations[name=”glaciation-project.eu/resource/limits/network”] | WL_NET_ALC | Network.Capacity | $.workloads.resources.network.allocated |
| Storage limit, gigabyte | K8s Deployment Resource<br/>$.spec.containers[].resources.limits.ephemeral-storage | WL_STR_ALC | Storage.Capacity | $.workloads.resources.storage.allocated |
| Memory limit, megabytes | K8s Deployment Resource<br/>$.spec.containers[name=”container-name”].resources.limits.memory | WL_MEM_ALC | RAM.Capacity | $.workloads.resources.memory.allocated |
| Energy limit, milliwatt | K8s Deployment Resource<br/>$.spec.metadata.annotations[name=”glaciation-project.eu/resource/limits/energy”] | WL_ENERGY_ALC | Energy.Capacity | $.workloads.resources.energy_index.allocated |
| CPU requests, cores | K8s Deployment Resource<br/>$.spec.containers[].resources.requests.cpu | WL_CPU_DEM | CPU.Allocated | $.workloads.resources.cpu.demanded |
| Memory requests, Mb | K8s Deployment Resource<br/>$.spec.containers[name=”container-name”].resources.requests.memory | WL_MEM_DEM | RAM.Allocated | $.workloads.resources.memory.demanded |
| GPU requests, unit | K8s Deployment Resource<br/>$.spec.containers[].resources.requests.”nvidia.com/gpu” | WL_GPU_DEM | GPU.Allocated | $.workloads.resources.gpu.demanded |
| Storage requests, GB | K8s Deployment Resource<br/>$.spec.containers[].resources.requests.ephemeral-storage | WL_STR_DEM | GPU.Allocated | $.workloads.resources.storage.demanded |
| Network requests, Mb | K8s Deployment Resource<br/>$.spec.metadata.annotations[name=”glaciation-project.eu/resource/requests/network”] | WL_NET_DEM | Network.Allocated | $.workloads.resources.network.demanded |
| Energy requests, milliwatts | K8s Deployment Resource<br/>$.spec.metadata.annotations[name=”glaciation-project.eu/resource/requests/energy”] | WL_ENERGY_DEM | Energy.Allocated | $.workloads.resources.energy_index.demanded |


# Sample K8S resources, Knowledge graphs and TradeOffService API

 - Worker Node
    - [K8s worker node](./0002-knowledge-graph-and-telemetry-specification-v3/workernode-k8s-node.yaml)
    - [Worker node metadata graph](./0002-knowledge-graph-and-telemetry-specification-v3/workernode-metadata-graph.jsonld)
    - [TradeOffService Node API](./0002-knowledge-graph-and-telemetry-specification-v3/workernode-tradeoff-service-api.json)

- Workload
    - [K8s Workload](./0002-knowledge-graph-and-telemetry-specification-v3/workload-k8s-deployment.yaml) (Deployment/ReplicaSet/Pod)
    - [Workload metadata graph](./0002-knowledge-graph-and-telemetry-specification-v3/workload-metadata-graph.jsonld)
    - [TradeOffService Workload API](./0002-knowledge-graph-and-telemetry-specification-v3/workload-tradeoff-service-api.json)

## References:

1. cAdvisor metrics [https://github.com/google/cadvisor/blob/master/docs/storage/prometheus.md](https://github.com/google/cadvisor/blob/master/docs/storage/prometheus.md)

2. Kubernetes metrics [https://kubernetes.io/docs/reference/instrumentation/metrics/](https://kubernetes.io/docs/reference/instrumentation/metrics/)

3. Allocatable Memory in kubernetes: [https://dev.to/ridaehamdani/understanding-allocatable-memory-and-cpu-in-kubernetes-nodes-4hbm#:~:text=In Kubernetes%2C allocatable resources refer,available CPU and memory resources](https://dev.to/ridaehamdani/understanding-allocatable-memory-and-cpu-in-kubernetes-nodes-4hbm#:~:text=In%20Kubernetes%2C%20allocatable%20resources%20refer,available%20CPU%20and%20memory%20resources)

4. Prometheus metrics parsing [https://docs.influxdata.com/influxdb/v1/supported_protocols/prometheus/](https://docs.influxdata.com/influxdb/v1/supported_protocols/prometheus/)

5. NVIDIA k8s-device-plugin [https://github.com/NVIDIA/k8s-device-plugin](https://github.com/NVIDIA/k8s-device-plugin)

6. GPU Metrics Exporter [https://github.com/NVIDIA/dcgm-exporter](https://github.com/NVIDIA/dcgm-exporter)
