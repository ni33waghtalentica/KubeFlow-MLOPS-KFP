"""Hello World pipeline — matches video/Gist: https://gist.github.com/iam-veeramalla/0e569b5e9da68736e51eda78a895212d"""
from kfp import dsl
from kfp import compiler


@dsl.component(base_image="python:3.10-slim")
def say_hello(name: str) -> str:
    """A simple component that says hello to a given name."""
    hello_text = f"Hello, {name}!"
    print(hello_text)
    return hello_text


@dsl.pipeline(
    name="hello-world-pipeline",
    description="A basic pipeline that prints a greeting.",
)
def hello_pipeline(recipient: str = "World") -> str:
    """Pipeline that runs the say_hello component."""
    hello_task = say_hello(name=recipient)
    return hello_task.output


if __name__ == "__main__":
    compiler.Compiler().compile(hello_pipeline, "hello_world_pipeline.yaml")
