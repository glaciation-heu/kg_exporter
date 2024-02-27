from unittest.mock import MagicMock

import pytest

from ..kg_exporter import KubernetesWatcher


@pytest.fixture
def mock_api_instance():
    # Create a mock Kubernetes API instance
    return MagicMock()


def test_watch_resources(mock_api_instance):
    # Mock the Kubernetes API responses
    mock_api_instance.list_namespaced_deployment.return_value.items = [
        create_mock_deployment("deployment1", "1"),
        create_mock_deployment("deployment2", "2"),
    ]
    mock_api_instance.list_namespaced_stateful_set.return_value.items = [
        create_mock_stateful_set("statefulset1", "3"),
        create_mock_stateful_set("statefulset2", "4"),
    ]
    mock_api_instance.list_namespaced_job.return_value.items = [
        create_mock_job("job1", "5"),
        create_mock_job("job2", "6"),
    ]

    # Create a Kubernetes watcher instance with the mock API instance
    watcher = KubernetesWatcher(mock_api_instance)

    # Call the watch_resources method
    watcher.watch_resources()


def create_mock_deployment(name, resource_version):
    # Create a mock Deployment object
    mock_deployment = MagicMock()
    mock_deployment.metadata.name = name
    mock_deployment.metadata.resource_version = resource_version
    return mock_deployment


def create_mock_stateful_set(name, resource_version):
    # Create a mock StatefulSet object
    mock_stateful_set = MagicMock()
    mock_stateful_set.metadata.name = name
    mock_stateful_set.metadata.resource_version = resource_version
    return mock_stateful_set


def create_mock_job(name, resource_version):
    # Create a mock Job object
    mock_job = MagicMock()
    mock_job.metadata.name = name
    mock_job.metadata.resource_version = resource_version
    return mock_job
