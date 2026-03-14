from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from prim_to_dae import prims_to_dae
import io
import json

app = Flask(__name__)
CORS(app)

# ─────────────────────────────────────────
#  Health check
# ─────────────────────────────────────────

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "message": "SL Prim to Mesh converter is running!"
    })

# ─────────────────────────────────────────
#  Main conversion endpoint
# ─────────────────────────────────────────

@app.route("/convert", methods=["POST"])
def convert():
    try:
        # get the prim data sent from LSL
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data received"}), 400

        prims = data.get("prims", [])

        if not prims:
            return jsonify({"error": "No prims in data"}), 400

        # convert to .dae
        dae_content = prims_to_dae(prims)

        # send back as a downloadable file
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

# ─────────────────────────────────────────
#  Run
# ─────────────────────────────────────────

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

4. Scroll down click **"Commit changes"** → **"Commit changes"** again

---

## Your repository should now have these 3 files:
```
sl-prim-to-mesh/
├── app.py
├── prim_to_dae.py
└── requirements.txt
