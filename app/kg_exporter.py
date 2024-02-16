import logging
from kubernetes import client, config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KubernetesWatcher:
    def __init__(self):
        # Initialize Kubernetes client
        config.load_kube_config()
        self.api_instance = client.AppsV1Api()

    def watch_resources(self):
        resource_types = ['Deployment', 'StatefulSet', 'Job']
        resource_version_mapping = {}
        for resource_type in resource_types:
            response = getattr(self.api_instance, f'list_namespaced_{resource_type.lower()}')('default')
            items = response.items
            resource_version_mapping[resource_type] = {item.metadata.name: item.metadata.resource_version for item in items}
            for item in items:
                logger.info(f"{resource_type} {item.metadata.name} version {item.metadata.resource_version}")

        while True:
            try:
                for resource_type in resource_types:
                    response = getattr(self.api_instance, f'list_namespaced_{resource_type.lower()}')('default', watch=True)
                    for event in response:
                        obj = event['object']
                        metadata = obj.get('metadata')
                        if metadata:
                            resource_name = metadata.get('name')
                            resource_version = metadata.get('resourceVersion')
                            if resource_name and resource_version:
                                logger.info(f"{event['type']} event for {resource_type} {resource_name}, version {resource_version}")
            except Exception as e:
                logger.error(f"An error occurred: {e}")

def main():
    watcher = KubernetesWatcher()
    watcher.watch_resources()

if __name__ == "__main__":
    main()
