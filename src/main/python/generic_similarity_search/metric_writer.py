import boto3


class Metric(object):
    def __init__(self, namespace: str, name: str):
        self.name = name
        self.namespace = namespace
        self.client = boto3.client("cloudwatch")

    def write_datapoint(self, value: int):
        self.client.put_metric_data(
            Namespace=self.namespace,
            MetricData=[
                {
                    "MetricName": self.name,
                    "Value": float(value),
                    "Unit": "None"
                }
            ]
        )
