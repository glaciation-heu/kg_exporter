# kg-exporter

![Version: 0.0.0](https://img.shields.io/badge/Version-0.0.0-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 0.0.0](https://img.shields.io/badge/AppVersion-0.0.0-informational?style=flat-square)

Kubernetes knowledge graph exporter service.

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| fullnameOverride | string | `""` |  |
| image.pullPolicy | string | `"IfNotPresent"` |  |
| image.repository | string | `""` |  |
| image.tag | string | `""` |  |
| imagePullSecrets | list | `[]` |  |
| ingressHostName | string | `"kg-exporter"` |  |
| livenessProbe.failureThreshold | int | `3` |  |
| livenessProbe.httpGet.path | string | `"/"` |  |
| livenessProbe.httpGet.port | int | `8080` |  |
| livenessProbe.httpGet.scheme | string | `"HTTP"` |  |
| livenessProbe.initialDelaySeconds | int | `15` |  |
| livenessProbe.periodSeconds | int | `10` |  |
| livenessProbe.timeoutSeconds | int | `5` |  |
| nameOverride | string | `""` |  |
| podAnnotations | object | `{}` |  |
| podLabels | object | `{}` |  |
| podSecurityContext | object | `{}` |  |
| readinessProbe.httpGet.path | string | `"/"` |  |
| readinessProbe.httpGet.port | int | `8080` |  |
| readinessProbe.httpGet.scheme | string | `"HTTP"` |  |
| readinessProbe.initialDelaySeconds | int | `15` |  |
| readinessProbe.periodSeconds | int | `10` |  |
| readinessProbe.timeoutSeconds | int | `5` |  |
| replicaCount | int | `1` |  |
| resources | object | `{}` |  |
| securityContext | object | `{}` |  |
| service.port | int | `8080` |  |
| service.type | string | `"ClusterIP"` |  |
| serviceAccount.annotations | object | `{}` |  |
| serviceAccount.automount | bool | `true` |  |
| serviceAccount.create | bool | `true` |  |
| serviceAccount.name | string | `""` |  |
| settings.builder.builder_tick_seconds | int | `60` | Periodicity of knolwedge graph building |
| settings.builder.is_single_slice | bool | `false` | Enables/Disables single slice per cluster or daemon set |
| settings.builder.node_port | int | `80` | DKG Slice service node port |
| settings.builder.queries.node_queries | list | [] | Prometheus node specific metrics queries |
| settings.builder.queries.pod_queries | list | [] | Prometheus pod specific metrics queries |
| settings.builder.single_slice_url | string | `"http://metadata-service:80"` | In case single DKG slice is enabled, this is the url of the single DKG slice |
| settings.k8s.in_cluster | bool | `true` | in cluster or out service cluster execution |
| settings.metadata.metadata_service_url | string | `"metadata-service"` | Metadata Service endpoint service name |
| settings.metadata.timeout_seconds | int | `20` | Metadata Service API timeout |
| settings.prometheus.endpoint_port | int | `8080` | KG exporter '/metrics' API port |
| settings.prometheus_client.url | string | `"prometheus.integration"` | Prometheus endpoint url |

----------------------------------------------
Autogenerated from chart metadata using [helm-docs v1.13.1](https://github.com/norwoodj/helm-docs/releases/v1.13.1)
