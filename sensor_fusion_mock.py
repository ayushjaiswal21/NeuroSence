"""
Sensor Fusion Strategy for Physiological Monitoring

This module implements the proposed logic for fusing HRV data (from MAX30102)
and skin conductance data (from GSR sensor).

Rules defined:
1. Low HRV + High GSR = High Stress / Arousal
2. High HRV + GSR spikes = Momentary surprise or micro-stress
3. High HRV + Low GSR = Resting state (No Stress)
4. Low HRV + Low GSR = Fatigue or cognitive load without emotional arousal
"""

import numpy as np

def evaluate_stress_state(hrv_score, gsr_conductivity):
    """
    Evaluates stress state based on HRV and GSR.
    
    Parameters:
    hrv_score (float): Normalized HRV score (e.g., RMSSD). Higher means better recovery.
    gsr_conductivity (float): Normalized GSR value. Higher means more sweating / arousal.
    
    Returns:
    str: The predicted physiological state.
    """
    
    hrv_threshold = 50.0 # Example threshold, to be calibrated to individual
    gsr_threshold = 0.5  # Example threshold
    
    hrv_is_high = hrv_score >= hrv_threshold
    gsr_is_high = gsr_conductivity >= gsr_threshold
    
    if not hrv_is_high and gsr_is_high:
        return "High Stress / Arousal"
    elif hrv_is_high and gsr_is_high:
        return "Momentary Surprise / Micro-stress"
    elif not hrv_is_high and not gsr_is_high:
        return "Fatigue / Cognitive Load"
    else:
        return "Resting / No Stress"

if __name__ == "__main__":
    print("Testing Sensor Fusion Logic:")
    # Low HRV, High GSR (Fight or flight response)
    print("State 1:", evaluate_stress_state(hrv_score=30.0, gsr_conductivity=0.8)) 
    
    # High HRV, High GSR (Sudden startle but physiologically recovered)
    print("State 2:", evaluate_stress_state(hrv_score=70.0, gsr_conductivity=0.9)) 
    
    # High HRV, Low GSR (Relaxed)
    print("State 3:", evaluate_stress_state(hrv_score=80.0, gsr_conductivity=0.2)) 
