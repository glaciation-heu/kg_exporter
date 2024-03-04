import argparse
import logging
import signal
import threading
from abc import ABC, abstractmethod

from kubernetes import client, config, watch
from kubernetes.client.models.v1_deployment_list import V1DeploymentList
from kubernetes.client.models.v1_job_list import V1JobList
from kubernetes.client.models.v1_stateful_set_list import V1StatefulSetList


class Resource(ABC):
    def __init__(self, api: client.AppsV1Api | client.BatchV1Api) -> None:
        self._api = api

    @abstractmethod
    def get_list(
        self,
        namespace: str,
        watch: bool,
    ) -> V1DeploymentList | V1StatefulSetList | V1JobList:
        raise NotImplementedError


class DeploymentResource(Resource):
    def __init__(self, api: client.AppsV1Api) -> None:
        self._api = api

    def get_list(
        self,
        namespace: str,
        watch: bool,
    ) -> V1DeploymentList:
        return self._api.list_namespaced_deployment(
            namespace=namespace,
            watch=watch,
        )


class StatefulSetResource(Resource):
    def __init__(self, api: client.AppsV1Api) -> None:
        self._api = api

    def get_list(
        self,
        namespace: str,
        watch: bool,
    ) -> V1StatefulSetList:
        return self._api.list_namespaced_stateful_set(
            namespace=namespace,
            watch=watch,
        )


class JobResource(Resource):
    def __init__(self, api: client.BatchV1Api) -> None:
        self._api = api

    def get_list(
        self,
        namespace: str,
        watch: bool,
    ) -> V1JobList:
        return self._api.list_namespaced_job(
            namespace=namespace,
            watch=watch,
        )


class KubernetesWatcher:
    namespace: str = "default"

    def __init__(self, resources: dict[str, Resource], logger: logging.Logger) -> None:
        self._resources = resources
        self._logger = logger

    def _watch_resource(self, resource_name: str, resource: Resource) -> None:
        try:
            for event in watch.Watch().stream(
                resource.get_list, namespace=self.namespace, watch=True
            ):
                obj = event["object"]
                metadata = obj.get("metadata")
                if metadata:
                    name = metadata.get("name")
                    version = metadata.get("resourceVersion")
                    if name and version:
                        self._logger.info(
                            f"{event['type']}: resource={resource_name}; "
                            f"name={name}, version={version}"
                        )
        except client.ApiException as e:
            self._logger.exception(e)

    def watch_resources(self) -> None:
        self._logger.info("Events:")

        threads = []
        for resource_name, resource in self._resources.items():
            thread = threading.Thread(
                target=self._watch_resource, args=(resource_name, resource)
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()


def run_watcher(incluster: bool, logger: logging.Logger) -> None:
    if incluster:
        config.load_incluster_config()
    else:
        config.load_kube_config()

    apps_api = client.AppsV1Api()
    batch_api = client.BatchV1Api()

    resources = {
        "Deployment": DeploymentResource(apps_api),
        "StatefulSet": StatefulSetResource(apps_api),
        "Job": JobResource(batch_api),
    }

    watcher = KubernetesWatcher(resources, logger)
    watcher.watch_resources()


def main() -> None:
    parser = argparse.ArgumentParser(description="Kubernetes watcher service")
    parser.add_argument(
        "--incluster",
        dest="incluster",
        action="store_true",
        help="Load a Kubernetes config from within a cluster",
    )
    args = parser.parse_args()

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    logger.addHandler(console_handler)

    run_watcher(args.incluster, logger)


if __name__ == "__main__":
    main()
