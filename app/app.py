"""
payment-service — Sample Flask web service
Used as the deployable application in the Release Pipeline Demo.
Simulates a payment gateway health/status API.
"""

from flask import Flask, jsonify
import os
import time

app = Flask(__name__)

APP_VERSION = os.environ.get("APP_VERSION", "1.0.0")
ENVIRONMENT = os.environ.get("DEPLOY_ENV", "dev")
START_TIME  = time.time()


@app.route("/")
def index():
    return jsonify({
        "service":     "payment-service",
        "version":     APP_VERSION,
        "environment": ENVIRONMENT,
        "status":      "running"
    })


@app.route("/health")
def health():
    """Health check endpoint — used by smoke tests and SLA monitoring."""
    uptime_seconds = round(time.time() - START_TIME, 2)
    return jsonify({
        "status":   "healthy",
        "version":  APP_VERSION,
        "env":      ENVIRONMENT,
        "uptime_s": uptime_seconds
    }), 200


@app.route("/ready")
def readiness():
    """Readiness probe — confirms app is ready to receive traffic."""
    return jsonify({"ready": True}), 200


@app.route("/payment/process", methods=["POST"])
def process_payment():
    """Stub payment processing endpoint."""
    return jsonify({
        "transaction_id": "TXN-DEMO-001",
        "status":         "accepted",
        "message":        "Payment queued for processing"
    }), 202


@app.route("/version")
def version():
    return jsonify({
        "version":     APP_VERSION,
        "environment": ENVIRONMENT,
        "build":       os.environ.get("BUILD_NUMBER", "local")
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = ENVIRONMENT == "dev"
    print(f"Starting payment-service v{APP_VERSION} on port {port} [{ENVIRONMENT}]")
    app.run(host="0.0.0.0", port=port, debug=debug)
