from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from prim_to_dae import prims_to_dae
import io
import json

app = Flask(__name__)
CORS(app)

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "message": "SL Prim to Mesh converter is running!"
    })

@app.route("/convert", methods=["POST", "GET"])
def convert():
    try:
        # try all possible ways to get the data
        raw = None

        # method 1 - from json
        if request.is_json:
            data = request.get_json(force=True, silent=True)
            if data:
                raw = data

        # method 2 - from raw body
        if not raw:
            body = request.get_data(as_text=True)
            if body:
                try:
                    raw = json.loads(body)
                except:
                    pass

        # method 3 - from query string
        if not raw:
            qs = request.args.get("data")
            if qs:
                try:
                    raw = json.loads(qs)
                except:
                    pass

        # method 4 - from form data
        if not raw:
            form_data = request.form.get("data")
            if form_data:
                try:
                    raw = json.loads(form_data)
                except:
                    pass

        if not raw:
            return jsonify({"error": "No data received"}), 400

        prims = raw.get("prims", [])
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
    app.run(host="0.0.0.0", port=5000)
