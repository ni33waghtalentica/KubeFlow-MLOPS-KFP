"""Sentiment Check pipeline — demo for text sentiment (test pipeline)."""
from kfp import dsl
from kfp import compiler


@dsl.component(base_image="python:3.10-slim")
def sentiment_step(text_input: str = "Hello world") -> str:
    """Demo component: simulates a sentiment result for the given text."""
    # Placeholder: in a real pipeline you'd call a model or API
    result = f"Sentiment Check: processed '{text_input[:50]}...' (demo)."
    print(result)
    return result


@dsl.pipeline(
    name="Sentiment Check",
    description="Demo pipeline for text sentiment analysis.",
)
def sentiment_check_pipeline(text_input: str = "Hello world") -> str:
    """Pipeline that runs the sentiment check component."""
    task = sentiment_step(text_input=text_input)
    return task.output


if __name__ == "__main__":
    compiler.Compiler().compile(sentiment_check_pipeline, "sentiment_check_pipeline.yaml")
