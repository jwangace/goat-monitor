import os
import requests
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)
GOAT_RPC_NODE = os.getenv("GOAT_RPC_NODE", "https://rpc.goat.network")

def json_rpc(method, params=[]):
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }
    try:
        response = requests.post(GOAT_RPC_NODE, json=payload, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data.get("result", None)
    except Exception as e:
        return None

@app.route("/status")
def status():
    batch_payload = [
        {
            "jsonrpc": "2.0",
            "method": "eth_syncing",
            "params": [],
            "id": 1
        },
        {
            "jsonrpc": "2.0",
            "method": "eth_blockNumber",
            "params": [],
            "id": 2
        },
        {
            "jsonrpc": "2.0",
            "method": "eth_chainId",
            "params": [],
            "id": 3
        }
    ]
    try:
        response = requests.post(GOAT_RPC_NODE, json=batch_payload, timeout=5)
        response.raise_for_status()
        results = {item["id"]: item.get("result") for item in response.json()}
        syncing_result = results.get(1)
        block_number_hex = results.get(2)
        chain_id_hex = results.get(3)
    except Exception:
        syncing_result = None
        block_number_hex = None
        chain_id_hex = None

    syncing = syncing_result not in [False, None]
    block_height = int(block_number_hex, 16) if block_number_hex else 0
    chain_id = int(chain_id_hex, 16) if chain_id_hex else 0

    return jsonify({
        "syncing": syncing,
        "block_height": block_height,
        "chain_id": chain_id
    })

@app.route("/")
def home():
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Goat Node Monitor</title>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background: #f9f9f9;
            padding: 40px;
            color: #333;
        }

        h1 {
            margin-bottom: 30px;
        }

        table {
            border-collapse: collapse;
            width: 100%;
            max-width: 700px;
            background: white;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        th, td {
            text-align: left;
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
        }

        th {
            background-color: #f2f2f2;
            font-weight: 600;
        }

        tr:hover {
            background-color: #f9f9f9;
        }

        .checkmark {
            color: green;
            font-size: 18px;
        }

        .crossmark {
            color: red;
            font-size: 18px;
        }
    </style>
</head>
<body>
    <h1>Goat Node Monitor</h1>
    <div class="rpc-url"><strong>{{ rpc_url }}</strong></div>
    <table>
        <thead>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Height</td>
                <td id="block_height">Loading...</td>
            </tr>
            <tr>
                <td>Chain ID</td>
                <td id="chain_id">Loading...</td>
            </tr>
            <tr>
                <td>Syncing</td>
                <td id="syncing">Loading...</td>
            </tr>
        </tbody>
    </table>

    <script>
        function fetchStatus() {
            $.getJSON("/status", function(data) {
                $("#block_height").text(data.block_height);
                $("#chain_id").text(data.chain_id);

                if (data.syncing) {
                    $("#syncing").text("Yes");
                } else {
                    $("#syncing").text("No");
                }
            }).fail(function() {
                $("#block_height, #chain_id, #syncing").text("Error");
            });
        }

        fetchStatus();
        setInterval(fetchStatus, 5000);
    </script>
</body>
</html>
""", rpc_url=GOAT_RPC_NODE)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)