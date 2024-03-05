# Kubernetes cluster RDF/Turtle knowledge graph sample

The following resources covered:
- [nodes turtle](./k8s-knowledge-graph/nodes.turtle), [master node diagram](./k8s-knowledge-graph/nodes.glaciation-mast01.png)
- workloads:
   - [deployments](./k8s-knowledge-graph/deployments.turtle) ([pic](./k8s-knowledge-graph/deployments.all.png)) with [replicasets](./k8s-knowledge-graph/replicasets.turtle)
   - [daemonsets](./k8s-knowledge-graph/daemonsets.turtle) ([pic](./k8s-knowledge-graph/daemonsets.kepler.png))
- [pods with containers](./k8s-knowledge-graph/pods.turtle), ([one pod sample pic](./k8s-knowledge-graph/pods.idrac-exporter.png))
- [workload telemetry](./k8s-knowledge-graph/workload-telemetry.turtle) ([pic](./k8s-knowledge-graph/workload-telemetry.png))) (assumming that telemetry is not part of the knowledge)

The knowledge graph is a snapshot of an entire test cluster.
It is in turtle format can be viewed using Turtle Editor/Viewer https://www.semantechs.co.uk/turtle-editor-viewer/

 