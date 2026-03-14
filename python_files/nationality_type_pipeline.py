"""Nationality type pipeline — demo pipeline for nationality classification."""
from kfp import dsl
from kfp import compiler


@dsl.component(base_image="python:3.10-slim")
def nationality_step(region: str = "global") -> str:
    """Demo component for nationality type pipeline."""
    msg = f"Nationality type pipeline: region '{region}'."
    print(msg)
    return msg


@dsl.pipeline(
    name="Nationality type",
    description="Pipeline for nationality type classification.",
)
def nationality_type_pipeline(region: str = "global") -> str:
    """Pipeline that runs the nationality type component."""
    task = nationality_step(region=region)
    return task.output


if __name__ == "__main__":
    compiler.Compiler().compile(nationality_type_pipeline, "nationality_type_pipeline.yaml")
