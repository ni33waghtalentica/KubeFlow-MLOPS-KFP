"""Viruses pipeline — demo pipeline for virus-related processing."""
from kfp import dsl
from kfp import compiler


@dsl.component(base_image="python:3.10-slim")
def viruses_step(category: str = "generic") -> str:
    """Demo component for viruses pipeline."""
    msg = f"Viruses pipeline: category '{category}'."
    print(msg)
    return msg


@dsl.pipeline(
    name="Viruses",
    description="Pipeline for virus-related analysis or classification.",
)
def viruses_pipeline(category: str = "generic") -> str:
    """Pipeline that runs the viruses component."""
    task = viruses_step(category=category)
    return task.output


if __name__ == "__main__":
    compiler.Compiler().compile(viruses_pipeline, "viruses_pipeline.yaml")
