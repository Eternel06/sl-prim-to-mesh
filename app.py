from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from prim_to_dae import prims_to_dae
import io
import json

app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "message": "SL Prim to Mesh converter is running!"
    })

@app.route("/convert", methods=["GET"])
def convert():
    try:
        raw = request.args.get("data")
        if not raw:
            return jsonify({"error": "No data received"}), 400
        try:
            data = json.loads(raw)
        except Exception as e:
            return jsonify({"error": "Invalid JSON: " + str(e)}), 400
        prims = data.get("prims", [])
        if not prims:
            return jsonify({"error": "No prims found"}), 400
        dae_content = prims_to_dae(prims)
        if not dae_content:
            return jsonify({"error": "DAE generation failed"}), 500
        dae_bytes = io.BytesIO(dae_content.encode("utf-8"))
        dae_bytes.seek(0)
        return send_file(
            dae_bytes,
            mimetype="application/octet-stream",
            as_attachment=True,
            download_name="prim_mesh.dae"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
