from unittest import TestCase

from app.core.builder.slice_strategy.single_slice_strategy import SingleSliceStrategy
from app.core.test_snapshot_base import SnapshotTestBase
from app.core.types import KGSliceId


class SingleSliceStrategyTest(TestCase, SnapshotTestBase):
    def test_split_empty(self) -> None:
        strategy = SingleSliceStrategy(metadata_url="http://metadata-service:80")
        resources = self.load_k8s_snapshot("empty")
        metrics = self.load_metric_snapshot("empty")
        actual = strategy.get_slices(resources, metrics)
        expected_slice_id = KGSliceId(node_ip="metadata-service", port=80)
        self.assertEqual({expected_slice_id}, actual.keys())

        inputs = actual[expected_slice_id]
        actual_names = inputs.resource.get_resource_names()
        self.assertEqual(actual_names, set())

        actual_metric_names = inputs.metrics.get_metric_names()
        self.assertEqual(actual_metric_names, set())

    def test_split_minimal(self) -> None:
        strategy = SingleSliceStrategy(metadata_url="http://metadata-service:80")
        resources = self.load_k8s_snapshot("minimal")
        metrics = self.load_metric_snapshot("minimal")
        actual = strategy.get_slices(resources, metrics)

        expected_slice_id = KGSliceId(node_ip="metadata-service", port=80)
        self.assertEqual({expected_slice_id}, actual.keys())

        inputs = actual[expected_slice_id]
        actual_names = inputs.resource.get_resource_names()
        self.assertEqual(
            {
                "glaciation-test-master01",
                "coredns",
                "coredns-787d4945fb",
                "coredns-787d4945fb-l85r5",
            },
            actual_names,
        )

        actual_metric_names = inputs.metrics.get_metric_names()
        self.assertEqual(
            {
                "eph_usage",
                "cpu_usage",
                "net_usage",
                "ram_usage",
                "pod_net_usage",
                "pod_cpu_usage",
                "pod_ram_usage",
                "pod_eph_usage",
            },
            actual_metric_names,
        )

    def test_split_multinode(self) -> None:
        strategy = SingleSliceStrategy(metadata_url="http://metadata-service:80")
        resources = self.load_k8s_snapshot("multinode")
        metrics = self.load_metric_snapshot("multinode")
        actual = strategy.get_slices(resources, metrics)

        expected_slice_id = KGSliceId(node_ip="metadata-service", port=80)
        self.assertEqual({expected_slice_id}, actual.keys())

        inputs = actual[expected_slice_id]
        actual_names = inputs.resource.get_resource_names()
        self.assertEqual(
            {
                "glaciation-test-master01",
                "coredns",
                "coredns-787d4945fb",
                "coredns-787d4945fb-l85r5",
                "kube-flannel-ds-848v8",
                "glaciation-pool-0",
                "init-vault-cluster-cbqhq",
                "kube-flannel-ds",
                "init-vault-cluster",
                "glaciation-pool-0-0",
                "tenant1-pool-0-1",
                "glaciation-test-worker01",
            },
            actual_names,
        )

        actual_metric_names = inputs.metrics.get_metric_names()
        self.assertEqual(
            {
                "eph_usage",
                "cpu_usage",
                "net_usage",
                "ram_usage",
                "pod_net_usage",
                "pod_cpu_usage",
                "pod_ram_usage",
                "pod_eph_usage",
                "gpu_usage",
            },
            actual_metric_names,
        )
