"""Data Summary pipeline — demo for dataset summary (test pipeline)."""
from kfp import dsl
from kfp import compiler


@dsl.component(base_image="python:3.10-slim")
def summary_step(dataset_name: str = "sample") -> str:
    """Demo component: returns a placeholder summary for the dataset."""
    summary = f"Data Summary: dataset '{dataset_name}' — rows: 1000, cols: 5 (demo)."
    print(summary)
    return summary


@dsl.pipeline(
    name="Data Summary",
    description="Demo pipeline for dataset summary statistics.",
)
def data_summary_pipeline(dataset_name: str = "sample") -> str:
    """Pipeline that runs the data summary component."""
    task = summary_step(dataset_name=dataset_name)
    return task.output


if __name__ == "__main__":
    compiler.Compiler().compile(data_summary_pipeline, "data_summary_pipeline.yaml")
