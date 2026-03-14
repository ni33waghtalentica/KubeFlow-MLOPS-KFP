"""Animal Species pipeline — classifies or lists animal species (demo)."""
from kfp import dsl
from kfp import compiler


@dsl.component(base_image="python:3.10-slim")
def animal_species_step(species_input: str = "mammals") -> str:
    """Demo component for animal species pipeline."""
    msg = f"Animal Species pipeline: processing '{species_input}'."
    print(msg)
    return msg


@dsl.pipeline(
    name="Animal Species",
    description="Pipeline for animal species classification or listing.",
)
def animal_species_pipeline(species_input: str = "mammals") -> str:
    """Pipeline that runs the animal species component."""
    task = animal_species_step(species_input=species_input)
    return task.output


if __name__ == "__main__":
    compiler.Compiler().compile(animal_species_pipeline, "animal_species_pipeline.yaml")
