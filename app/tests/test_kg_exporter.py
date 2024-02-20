import unittest
from unittest.mock import patch, MagicMock
from kg_exporter import KubernetesWatcher

class TestKubernetesWatcher(unittest.TestCase):
    def setUp(self):
        self.watcher = KubernetesWatcher()

    @patch('kg_exporter.client.AppsV1Api.list_namespaced_deployment')
    @patch('kg_exporter.client.AppsV1Api.list_namespaced_stateful_set')
    @patch('kg_exporter.client.BatchV1Api.list_namespaced_job')
    def test_watch_resources(self, mock_list_job, mock_list_stateful_set, mock_list_deployment):
        mock_list_deployment.return_value.items = [
            self.create_mock_deployment('deployment1', '1'),
            self.create_mock_deployment('deployment2', '2')
        ]
        mock_list_stateful_set.return_value.items = [
            self.create_mock_stateful_set('statefulset1', '3'),
            self.create_mock_stateful_set('statefulset2', '4')
        ]
        mock_list_job.return_value.items = [
            self.create_mock_job('job1', '5'),
            self.create_mock_job('job2', '6')
        ]

        # Mock the infinite loop to prevent it from running indefinitely
        with patch('kg_exporter.KubernetesWatcher.watch_resources', side_effect=KeyboardInterrupt):
            self.watcher.watch_resources()

        # Create a Kubernetes watcher instance
        watcher = KubernetesWatcher()

        # Call the watch_resources method
        watcher.watch_resources()

        # Add assertions based on expected behavior of the watcher
        # For example, assert that logging functions were called with expected arguments
        mock_list_deployment.assert_called_once_with('default', watch=True)
        mock_list_stateful_set.assert_called_once_with('default', watch=True)
        mock_list_job.assert_called_once_with('default', watch=True)

    def create_mock_deployment(self, name, resource_version):
        mock_deployment = MagicMock()
        mock_deployment.metadata.name = name
        mock_deployment.metadata.resource_version = resource_version
        return mock_deployment

    def create_mock_stateful_set(self, name, resource_version):
        mock_stateful_set = MagicMock()
        mock_stateful_set.metadata.name = name
        mock_stateful_set.metadata.resource_version = resource_version
        return mock_stateful_set

    def create_mock_job(self, name, resource_version):
        mock_job = MagicMock()
        mock_job.metadata.name = name
        mock_job.metadata.resource_version = resource_version
        return mock_job

if __name__ == '__main__':
    unittest.main()