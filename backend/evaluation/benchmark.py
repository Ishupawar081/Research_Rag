import sys
import os

sys.path.append(os.getcwd())

from backend.evaluation.evaluator import run_evaluation
from backend.evaluation.regression import check_regression

def run_stage(stage):
    print(f"==================================================")
    print(f" RUNNING EVALUATION STAGE: {stage}")
    print(f"==================================================")
    
    if stage == "dev":
        dataset = "backend/evaluation/datasets/development_set.json"
    elif stage == "val":
        dataset = "backend/evaluation/datasets/validation_set.json"
    elif stage == "test":
        import json
        with open("backend/data/registry/papers.json", "r") as f:
            papers = json.load(f)
        all_pids = [p["paper_id"] for p in papers]
        dataset = "backend/evaluation/datasets/test_set_temp.json"
        with open(dataset, "w") as f:
            json.dump(all_pids, f)
    else:
        print("Invalid stage.")
        return
        
    # Get the latest iteration
    iteration = 1
    if os.path.exists("backend/evaluation/reports/benchmark_history.json"):
        import json
        with open("backend/evaluation/reports/benchmark_history.json") as f:
            hist = json.load(f)
            if hist:
                iteration = hist[-1]["iteration"] + 1
                
    metrics = run_evaluation(dataset, iteration)
    check_regression(metrics)
    
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", type=str, default="dev", choices=["dev", "val", "test"])
    args = parser.parse_args()
    
    run_stage(args.stage)
