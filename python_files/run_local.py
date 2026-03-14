#!/usr/bin/env python3
"""Run the Iris KFP pipeline locally using kfp.local (Docker required)."""
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def main():
    try:
        from kfp import local
    except ImportError:
        print("ERROR: kfp not installed. Run: pip install kfp")
        sys.exit(1)

    try:
        from iris_pipeline import iris_pipeline
    except ImportError as e:
        print(f"ERROR: Could not import iris_pipeline: {e}")
        sys.exit(1)

    try:
        local.init(runner=local.DockerRunner(), pipeline_root="./local_outputs")
    except Exception as e:
        print(f"ERROR: Failed to init Docker runner (is Docker running?): {e}")
        sys.exit(1)

    print("Running iris-no-artifacts-pipeline locally...")
    try:
        iris_pipeline()
        # Pipeline completed (accuracy is already printed by the train-model task)
        print("Pipeline finished successfully.")
        return 0
    except Exception as e:
        print(f"ERROR: Pipeline run failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    sys.exit(main())
