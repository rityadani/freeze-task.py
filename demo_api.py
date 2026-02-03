"""
Demo API Interface for Live Website Integration
Exposes RL decisions in demo-friendly JSON format
"""

from flask import Flask, request, jsonify
from rl_decision_brain import RLDecisionBrain, Environment, EventType
import json
import logging

app = Flask(__name__)
rl_brain = RLDecisionBrain(demo_mode=True)

# Configure logging
logging.basicConfig(level=logging.INFO)

@app.route('/api/decision', methods=['POST'])
def make_decision():
    """
    Demo endpoint: Simulate runtime event and get RL decision
    Expected input: {"environment": "dev|stage|prod", "event_type": "crash|overload|false_failure", "event_data": {}}
    """
    try:
        data = request.get_json()
        
        # Parse input
        env = Environment(data['environment'])
        event_type = EventType(data['event_type'])
        event_data = data.get('event_data', {})
        
        # Get RL decision
        decision = rl_brain.make_decision(env, event_type, event_data)
        
        # Format for demo display
        demo_response = {
            "runtime_event": {
                "environment": decision["environment"],
                "type": decision["event_type"],
                "data": decision["event_data"],
                "timestamp": decision["timestamp"]
            },
            "rl_decision": {
                "proposed_action": decision["proposed_action"],
                "final_action": decision["final_action"],
                "action_filtered": decision["action_filtered"],
                "reasoning": f"Deterministic decision for {decision['event_type']} in {decision['environment']}"
            },
            "safety_result": {
                "executed": decision["final_action"] != "noop",
                "refused": decision["action_filtered"],
                "safe_for_demo": True
            },
            "system_status": {
                "demo_mode": decision["demo_mode"],
                "learning_disabled": not decision["learning_enabled"],
                "deterministic": True
            }
        }
        
        return jsonify(demo_response)
        
    except Exception as e:
        logging.error(f"Decision API error: {str(e)}")
        return jsonify({"error": str(e)}), 400

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current system status for demo monitoring"""
    status = rl_brain.get_system_status()
    return jsonify(status)

@app.route('/api/demo/scenarios', methods=['GET'])
def get_demo_scenarios():
    """Return predefined demo scenarios for testing"""
    scenarios = [
        {
            "name": "Dev Crash Recovery",
            "input": {"environment": "dev", "event_type": "crash", "event_data": {"service": "api-server"}},
            "expected": "restart"
        },
        {
            "name": "Stage Overload Scaling", 
            "input": {"environment": "stage", "event_type": "overload", "event_data": {"cpu": 85}},
            "expected": "scale_up"
        },
        {
            "name": "Prod Conservative Response",
            "input": {"environment": "prod", "event_type": "overload", "event_data": {"memory": 90}},
            "expected": "noop"
        },
        {
            "name": "False Failure Ignored",
            "input": {"environment": "prod", "event_type": "false_failure", "event_data": {"alert": "network_blip"}},
            "expected": "noop"
        }
    ]
    return jsonify({"scenarios": scenarios})

if __name__ == '__main__':
    print("🚀 RL Decision Brain Demo API Starting...")
    print("📍 Demo Mode: ENABLED")
    print("🔒 Learning: FROZEN") 
    print("⚡ Behavior: DETERMINISTIC")
    app.run(host='0.0.0.0', port=5000, debug=False)