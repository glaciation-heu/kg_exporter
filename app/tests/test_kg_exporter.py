from typing import cast

import sys
from unittest.mock import MagicMock, call, patch

import pytest
from kubernetes import client
from kubernetes.client.models.v1_deployment_list import V1DeploymentList
from kubernetes.client.models.v1_job_list import V1JobList
from kubernetes.client.models.v1_stateful_set_list import V1StatefulSetList

from ..kg_exporter import (
    DeploymentResource,
    JobResource,
    KubernetesWatcher,
    Resource,
    StatefulSetResource,
    main,
    run_watcher,
)


@pytest.fixture
def logger() -> MagicMock:
    return MagicMock()


@pytest.fixture
def api() -> MagicMock:
    return MagicMock()


@pytest.fixture
def resources() -> dict[str, MagicMock]:
    return {
        "Deployment": MagicMock(spec=Resource),
        "StatefulSet": MagicMock(spec=Resource),
        "Job": MagicMock(spec=Resource),
    }


class TestDeploymentResource:
    def test_get_list(self, api: MagicMock) -> None:
        mock_response = V1DeploymentList(items=[{"metadata": {"name": "test_name"}}])
        api.list_namespaced_deployment.return_value = mock_response

        resource = DeploymentResource(api)
        result = resource.get_list(namespace="test_namespace", watch=True)

        assert result == mock_response
        api.list_namespaced_deployment.assert_called_once_with(
            namespace="test_namespace", watch=True
        )


class TestStatefulSetResource:
    def test_get_list(self, api: MagicMock) -> None:
        mock_response = V1StatefulSetList(items=[{"metadata": {"name": "test_name"}}])
        api.list_namespaced_stateful_set.return_value = mock_response

        resource = StatefulSetResource(api)
        result = resource.get_list(namespace="test_namespace", watch=True)

        assert result == mock_response
        api.list_namespaced_stateful_set.assert_called_once_with(
            namespace="test_namespace", watch=True
        )


class TestJobResource:
    def test_get_list(self, api: MagicMock) -> None:
        mock_response = V1JobList(items=[{"metadata": {"name": "test_name"}}])
        api.list_namespaced_job.return_value = mock_response

        resource = JobResource(api)
        result = resource.get_list(namespace="test_namespace", watch=True)

        assert result == mock_response
        api.list_namespaced_job.assert_called_once_with(
            namespace="test_namespace", watch=True
        )


class TestKubernetesWatcher:
    def test_watch_resource(self, resources: MagicMock, logger: MagicMock) -> None:
        mock_watch = MagicMock()
        mock_watch().stream.return_value = [
            {
                "type": "ADDED",
                "object": {"metadata": {"name": "test_name", "resourceVersion": "1"}},
            },
            {
                "type": "MODIFIED",
                "object": {"metadata": {"name": "test_name", "resourceVersion": "2"}},
            },
            {
                "type": "DELETED",
                "object": {"metadata": {"name": "test_name", "resourceVersion": "3"}},
            },
        ]

        watcher = KubernetesWatcher(resources, logger)
        with patch("kubernetes.watch.Watch", mock_watch):
            watcher._watch_resource("Deployment", resources["Deployment"])

        mock_watch().stream.assert_called_once_with(
            resources["Deployment"].get_list,
            namespace=watcher.namespace,
            watch=True,
        )

        assert logger.info.call_count == 3
        assert logger.info.call_args_list == [
            call("ADDED: resource=Deployment; name=test_name, version=1"),
            call("MODIFIED: resource=Deployment; name=test_name, version=2"),
            call("DELETED: resource=Deployment; name=test_name, version=3"),
        ]

    def test_watch_resources_exception(
        self, resources: MagicMock, logger: MagicMock
    ) -> None:
        watcher = KubernetesWatcher(resources, logger)
        with patch("kubernetes.watch.Watch", side_effect=client.ApiException()):
            watcher._watch_resource("Deployment", resources["Deployment"])

        logger.exception.assert_called_once()

    @patch("app.kg_exporter.KubernetesWatcher._watch_resource")
    def test_watch_resources(
        self,
        mock_watch_resource: MagicMock,
        resources: MagicMock,
        logger: MagicMock,
    ) -> None:
        watcher = KubernetesWatcher(resources, logger)
        watcher.watch_resources()

        logger.info.assert_any_call("Events:")
        cast(MagicMock, watcher._watch_resource).assert_has_calls(
            [
                call(resource_name, resource)
                for resource_name, resource in resources.items()
            ]
        )


class TestRunWatcher:
    @patch("kubernetes.config.load_incluster_config")
    @patch("app.kg_exporter.KubernetesWatcher")
    def test_incluster(
        self,
        mock_watcher: MagicMock,
        mock_load_incluster_config: MagicMock,
        logger: MagicMock,
    ) -> None:
        run_watcher(incluster=True, logger=logger)

        mock_load_incluster_config.assert_called_once()

        mock_watcher.assert_called_once()
        args, kwargs = mock_watcher.call_args
        resources = args[0]

        assert args[1] == logger

        assert "Deployment" in resources
        assert "StatefulSet" in resources
        assert "Job" in resources

        assert isinstance(resources["Deployment"], DeploymentResource)
        assert isinstance(resources["StatefulSet"], StatefulSetResource)
        assert isinstance(resources["Job"], JobResource)

        mock_watcher.return_value.watch_resources.assert_called_once()

    @patch("kubernetes.config.load_kube_config")
    @patch("app.kg_exporter.KubernetesWatcher")
    def test_kube(
        self,
        mock_watcher: MagicMock,
        mock_load_kube_config: MagicMock,
        logger: MagicMock,
    ) -> None:
        run_watcher(incluster=False, logger=logger)

        mock_load_kube_config.assert_called_once()

        mock_watcher.assert_called_once()
        mock_watcher.return_value.watch_resources.assert_called_once()


class TestMain:
    @patch.object(sys, "argv", ["kg_exporter.py"])
    @patch("logging.getLogger")
    @patch("app.kg_exporter.run_watcher")
    def test_common(
        self, mock_run_watcher: MagicMock, mock_get_logger: MagicMock
    ) -> None:
        main()
        mock_run_watcher.assert_called_once_with(
            False,
            mock_get_logger.return_value,
        )

    @patch.object(sys, "argv", ["kg_exporter.py", "--incluster"])
    @patch("logging.getLogger")
    @patch("app.kg_exporter.run_watcher")
    def test_incluster(
        self, mock_run_watcher: MagicMock, mock_get_logger: MagicMock
    ) -> None:
        main()
        mock_run_watcher.assert_called_once_with(
            True,
            mock_get_logger.return_value,
        )
