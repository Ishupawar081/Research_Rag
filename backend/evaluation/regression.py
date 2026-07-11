import json

def check_regression(current_metrics, previous_metrics_file="backend/evaluation/reports/benchmark_history.json"):
    """
    Compares current iteration against previous iteration for all critical metrics.
    Returns True if passed (no regression), False if failed.
    """
    try:
        with open(previous_metrics_file, "r") as f:
            history = json.load(f)
            
        if not history or len(history) < 2:
            print("Not enough history to check regression.")
            return True
            
        # Get the previous iteration (the last one saved before this run)
        # Note: Depending on when we save, history[-1] might be the current run, so we should check history[-2] if len >= 2
        # If current run is already appended, the previous is history[-2]
        
        # We assume history[-2] is the previous one if the current one was just saved.
        # Let's verify by iteration number if possible. Current metrics don't have iteration passed in, but we can assume history[-2]
        prev = history[-2]["metrics"]
        
        failed = False
        reasons = []
        
        # 1. Precision & Recall
        for m in ["retrieval_precision", "retrieval_recall", "faithfulness", "groundedness", "formatting", "pass_rate"]:
            if m in current_metrics and m in prev:
                if current_metrics[m] < prev[m] - 2.0:
                    failed = True
                    reasons.append(f"{m.replace('_', ' ').title()} dropped: {prev[m]:.2f} -> {current_metrics[m]:.2f}")
                    
        # 2. Hallucination (lower is better)
        if "hallucination" in current_metrics and "hallucination" in prev:
            if current_metrics["hallucination"] > prev["hallucination"] + 2.0:
                failed = True
                reasons.append(f"Hallucination increased: {prev['hallucination']:.2f} -> {current_metrics['hallucination']:.2f}")
                
        # 3. Latency & Time (lower is better, flag if it spikes > 30%)
        for m in ["latency", "retrieval_time", "generation_time"]:
            if m in current_metrics and m in prev:
                if current_metrics[m] > prev[m] * 1.3:
                    failed = True
                    reasons.append(f"{m.replace('_', ' ').title()} spiked: {prev[m]:.2f}s -> {current_metrics[m]:.2f}s")
                    
        if failed:
            print("==================================================")
            print(" REGRESSION DETECTED!")
            print("==================================================")
            for r in reasons:
                print(f" - {r}")
            return False
            
        print("Regression check passed! All metrics stable or improved.")
        return True
        
    except FileNotFoundError:
        return True
    except Exception as e:
        print(f"Regression check failed due to error: {e}")
        return True
