from kubernetes import client, config


class KubernetesWatcher:
    def __init__(self, api_instance):
        self.api_instance = api_instance

    def watch_resources(self):
        resource_types = ["Deployment", "StatefulSet", "Job"]
        for resource_type in resource_types:
            response = getattr(
                self.api_instance, f"list_namespaced_{resource_type.lower()}"
            )("default")
            items = response.items
            for item in items:
                print(
                    f"{resource_type} {item.metadata.name} \
                        version {item.metadata.resource_version}"
                )

        while True:
            try:
                for resource_type in resource_types:
                    response = getattr(
                        self.api_instance,
                        f"\
                            list_namespaced_{resource_type.lower()}",
                    )("default", watch=True)
                    for event in response:
                        obj = event["object"]
                        metadata = obj.get("metadata")
                        if metadata:
                            resource_name = metadata.get("name")
                            resource_version = metadata.get("resourceVersion")
                            if resource_name and resource_version:
                                print(
                                    f"{event['type']} event for \
                                        {resource_type} \
                                        {resource_name} \
                                            , version {resource_version}"
                                )
            except Exception as e:
                print(f"An error occurred: {e}")


def main():
    # Initialize Kubernetes client
    config.load_kube_config()
    api_instance = client.AppsV1Api()

    # Create a Kubernetes watcher instance with the injected client
    watcher = KubernetesWatcher(api_instance)
    watcher.watch_resources()


if __name__ == "__main__":
    main()
