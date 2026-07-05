# SPDX-License-Identifier: Apache-2.0
"""Calculate confidence score from pipeline metrics payload."""

import json
import sys

def calculate_confidence_score(report_data):
    scores = report_data["scores"]
    weights = {
        "correctness": 0.35,
        "architecture": 0.20,
        "regression": 0.20,
        "performance": 0.15,
        "coverage": 0.10
    }
    
    total_score = sum(scores[key] * weights[key] for key in weights)
    
    level = 0
    if total_score >= 95.0 and scores["correctness"] == 100.0 and scores["regression"] == 100.0:
        level = 5
    elif total_score >= 85.0 and scores["correctness"] == 100.0:
        level = 4
    elif total_score >= 70.0:
        level = 3
    elif total_score >= 50.0:
        level = 2
    elif total_score >= 30.0:
        level = 1
        
    return round(total_score, 2), level

if __name__ == "__main__":
    mock_payload = {
        "checkpoint_id": "check-98ab21",
        "scores": {
            "correctness": 100.0,
            "architecture": 100.0,
            "regression": 100.0,
            "performance": 95.0,
            "coverage": 80.0
        }
    }
    
    score, level = calculate_confidence_score(mock_payload)
    
    report = {
        "checkpoint_id": mock_payload["checkpoint_id"],
        "weighted_confidence_score": score,
        "verification_level": level,
        "status": "APPROVED" if level >= 4 else "FAILED"
    }
    
    print(json.dumps(report, indent=2))
