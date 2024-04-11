
# Knowledge Graph and telemetry specification

# Worker Node

Terminology:

- Capacity - the maximum allocatable units of resource on the kubernetes worker node.

Energy consumption: converting joules_total (Counter) to milliwatts.
Average using window of 5 minutes (300 seconds):

- irate(kepler_node_platform_joules_total[300s]) / 300 = watts
- irate(kepler_node_platform_joules_total[300s]) *1000 / 300 = milliwatts

| Metric | Source | Synthetic Data Generator | Knowledge graph path | Tradeoff Service, (JsonPath) |
| --- | --- | --- | --- | --- |
| Node energy index, milliwatt | Node resource:<br/> $.metadata.annotations.['glaciation-project.eu/metric/node-energy-index'] |  | node-energy-index | $.worker_nodes.energy_index |
| Node CPU capacity max, cores | Node resource:<br/> $.status.allocatable.cpu | WN_CPU_MAX_CAPACITY | cpu-capacity-max | $.worker_nodes.resources.cpu.max |
| Node memory capacity max, Mb | Node resource:<br/> $.status.allocatable.memory | WN_MEM_MAX_CAPACITY | ram-capacity-max | $.worker_nodes.resources.memory.max |
| Node gpu capacity max, Flops | Not available yet | WN_GPU_MAX_CAPACITY | gpu-capacity-max | $.worker_nodes.resources.gpu.max |
| Node Storage capacity max (ephemeral storage), GB | TBD, (ephemeral storage helm chart) | WN_STR_MAX_CAPACITY | storage-capacity-max | $.worker_nodes.resources.storage.max |
| Node network capacity max, GB per second | Not available yet | WN_NET_MAX_CAPACITY | network-bandwidth-max | $.worker_nodes.resource.network.max |
| Node energy consumption, joules | Source: kepler:<br/> kepler_node_joules_total{node=”glaciation-testm1w5-worker01”} | ENERGY_CONSUMPTION_MIN, ENERGY_CONSUMPTION_MAX, ENERGY_CONSUMPTION_MEDIAN, ENERGY_CONSUMPTION_MEAN | node-energy-consumption | $.worker_nodes.energy.consumed |
| Node CPU available, core seconds | Source: node exporter: sum(rate(node_cpu_seconds_total{mode="idle", node="glaciation-testm1w5-worker01"}[5m])) | WN_CPU_AVAILABLE | cpu-capacity-available | $.worker_nodes.resources.cpu.available |
| Node Memory available, Mb | Source: node exporter:<br/> node_memory_MemFree_bytes{instance="glaciation-testm1w5-worker01", app_kubernetes_io_component="metrics"} | WN_MEM_AVAILABLE  | ram-capacity-available | $.worker_nodes.resources.memory.available |
| Node GPU available, flops | Not available yet | WN_GPU_AVAILABLE | gpu-capacity-available | $.worker_nodes.resources.gpu.available |
| Network Storage available (ephemeral), Mb | cAdvisor metric:<br/> container_fs_usage_bytes{instance="glaciation-testm1w5-worker01"}/ (1024 * 1024) | WN_STR_AVAILABLE | storage-capacity-available | $.worker_nodes.resources.storage.available |
| Node Network available, Mb | TBD  | WN_NET_AVAILABLE | network-bandwidth-available | $.worker_nodes.resources.network.available |


# Workload

Terminology and interpretation:

- Used - how much resource units is consumed (usage in terms of kubernetes - cAdvisor source)
- Demanded - How much of resource units a user requests for a pod (”requests” in terms of kubernetes)
- Allocated - How much of a resources is maximally allowed for a pod (limits in terms of kubernetes, It can also be configured on the level of cluster. To be researched)

For every metric in the table below promql query returns instant. To convert it into min, max, median and average it is necessary to wrap this query into the \<agg\>_over_time function with required time window.

- Minimum - min_over_time(\<instant subquery\>[\<window\>:\<resolution\>])
- Maximum - max_over_time(\<instant subquery\>[\<window\>:\<resolution\>])
- Average - avg_over_time(\<instant subquery\>[\<window\>:\<resolution\>])
- Median - quantile_over_time(\<instant subquery\>[\<window\>:\<resolution\>], 0.5)

Example:

- Instant query:

```promql
sum(
	rate(
		container_network_receive_bytes_total{pod="kube-flannel-ds-7wjqv"}[5m]
	)
)
```

- Aggregated over time query with 1 hour window and 1 minute resolution:

```promql
avg_over_time(
	sum(
		rate(
			container_network_receive_bytes_total{pod="kube-flannel-ds-7wjqv"}[5m]
		)
	)[1h:1m]
)
```

| Metric description | Prometheus query | Synthetic Data Generator | Knowledge graph, measurement description | Tradeoff Service |
| --- | --- | --- | --- | --- |
| Network received usage, Mb | cAdvisor:<br/> sum(rate(container_network_receive_bytes_total[5m])) by (pod) / (1024 * 1024) | WL_NET_REC_USG_AVG, WL_NET_REC_USG_MED, WL_NET_REC_USG_MAX, WL_NET_REC_USG_MIN | network-received |  |
| Network transfer usage minimum, Mbit per second | cAdvisor: sum(rate(container_network_transmit_bytes_total[5m])) by (pod) | WL_NET_TRN_USG_MIN, WL_NET_TRN_USG_MAX, WL_NET_TRN_USG_MED, WL_NET_TRN_USG_AVG | network-transferred |  |
| Storage read usage, Mb per second | cAdvisor:<br/> sum(rate(container_fs_reads_bytes_total[5m])) by (pod,device) / (1024 * 1024) | WL_STR_RED_USG_AVG, WL_STR_RED_USG_MAX, WL_STR_RED_USG_MIN, WL_STR_RED_USG_MED | storage-read |  |
| Storage write usage, MB per second | cAdvisor:<br/> sum(rate(container_fs_writes_bytes_total[5m])) by (pod,device) | WL_STR_WRT_USG_MIN, WL_STR_WRT_USG_MAX, WL_STR_WRT_USG_MED, WL_STR_WRT_USG_AVG | storage-write |  |
| Cpu usage minimum, unit: cores seconds | cAdvisor:<br/> sum(rate(container_cpu_usage_seconds_total[5m])) by (pod) | WL_CPU_USG_MIN, WL_CPU_USG_MAX, WL_CPU_USG_MED, WL_CPU_USG_AVG | cpu-used |  |
| Memory usage, Mb (and can be fractional) | cAdvisor:<br/> sum(container_memory_working_set_bytes) by (pod) /(1024*1024) | WL_MEM_USG_MIN, WL_MEM_USG_MAX, WL_MEM_USG_MED, WL_MEM_USG_AVG | ram-used |  |
| GPU usage, flops | Not available, device specific k8s plugin | WL_GPU_USG_MIN, WL_GPU_USG_MAX, WL_GPU_USG_MED, WL_GPU_USG_AVG | gpu-used |  |
| CPU limit, cores | K8s Deployment Resource: $.spec.containers[].resources.limits.cpu | WL_CPU_ALC | cpu-limits |  |
| GPU limit, flops | K8s Deployment Resource: $.spec.metadata.annotations[name=”glaciation-project.eu/resource/limits/gpu”] | WL_GPU_ALC | gpu-limits |  |
| Network limit, megabyte | K8s Deployment Resource:<br/> $.spec.metadata.annotations[name=”glaciation-project.eu/resource/limits/network”] | WL_NET_ALC | network-limits |  |
| Storage limit, gigabyte | K8s Deployment Resource:<br/> $.spec.containers[].resources.limits.ephemeral-storage | WL_STR_ALC | storage-limits |  |
| Memory limit, megabytes | K8s Deployment Resource:<br/> $.spec.containers[name=”container-name”].resources.limits.memory | WL_MEM_ALC | memory-limits |  |
| Energy limit, milliwatt | K8s Deployment Resource:<br/> $.spec.metadata.annotations[name=”glaciation-project.eu/resource/limits/energy”] | WL_ENERGY_ALC | energy-limits |  |
| CPU requests, cores | K8s Deployment Resource: $.spec.containers[].resources.requests.cpu | WL_CPU_DEM | cpu-requests |  |
| Memory requests, Mb | K8s Deployment Resource:<br/> $.spec.containers[name=”container-name”].resources.requests.memory | WL_MEM_DEM | ram-requests |  |
| GPU requests, flops | K8s Deployment Resource:<br/> $.spec.metadata.annotations[name=”glaciation-project.eu/resource/requests/gpu”] | WL_GPU_DEM | gpu-requests |  |
| Storage requests, GB | K8s Deployment Resource:<br/> $.spec.containers[].resources.requests.ephemeral-storage | WL_STR_DEM | storage-requests |  |
| Network requests, Mb | K8s Deployment Resource:<br/> $.spec.metadata.annotations[name=”glaciation-project.eu/resource/requests/network”] | WL_NET_DEM | network-requests |  |
| Energy requests, milliwatts | K8s Deployment Resource:<br/> $.spec.metadata.annotations[name=”glaciation-project.eu/resource/requests/energy”] | WL_ENERGY_DEM | energy-requests |  |


# Sample K8S resources, Knowledge graphs and TradeOffService API

 - Worker Node
    - [K8s worker node](./0001-knowledge-graph-and-telemetry-specification/workernode-k8s-node.yaml)
    - [Worker node metadata graph](./0001-knowledge-graph-and-telemetry-specification/workernode-metadata-graph.jsonld)
    - [TradeOffService Node API](./0001-knowledge-graph-and-telemetry-specification/workernode-tradeoff-service-api.json)

- Workload
    - [K8s Workload](./0001-knowledge-graph-and-telemetry-specification/workload-k8s-deployment.yaml) (Deployment/ReplicaSet/Pod)
    - [Workload metadata graph](./0001-knowledge-graph-and-telemetry-specification/workload-metadata-graph.jsonld)
    - [TradeOffService Workload API](./0001-knowledge-graph-and-telemetry-specification/workload-tradeoff-service-api.json)


## References:

1. cAdvisor metrics [https://github.com/google/cadvisor/blob/master/docs/storage/prometheus.md](https://github.com/google/cadvisor/blob/master/docs/storage/prometheus.md)
2. Kubernetes metrics

    [https://kubernetes.io/docs/reference/instrumentation/metrics/](https://kubernetes.io/docs/reference/instrumentation/metrics/)

3. Allocatable Memory in kubernetes:

    [https://dev.to/ridaehamdani/understanding-allocatable-memory-and-cpu-in-kubernetes-nodes-4hbm#:~:text=In Kubernetes%2C allocatable resources refer,available CPU and memory resources](https://dev.to/ridaehamdani/understanding-allocatable-memory-and-cpu-in-kubernetes-nodes-4hbm#:~:text=In%20Kubernetes%2C%20allocatable%20resources%20refer,available%20CPU%20and%20memory%20resources)

4. Prometheus metrics parsing [https://docs.influxdata.com/influxdb/v1/supported_protocols/prometheus/](https://docs.influxdata.com/influxdb/v1/supported_protocols/prometheus/)
