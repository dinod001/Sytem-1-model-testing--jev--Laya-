from flask import Flask, request, jsonify
import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='.', static_url_path='')

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

try:
    import laya
    print("Loading Laya model locally...")
    # Load the english laya model
    laya_agent = laya.load("convaiinnovations/laya")
    print("Laya loaded successfully.")
except ImportError:
    laya_agent = None
    print("Laya not installed. Run 'pip install laya' first.")

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/benchmark', methods=['POST'])
def benchmark():
    if not OPENROUTER_API_KEY:
        return jsonify({"error": "OPENROUTER_API_KEY environment variable is not set."}), 400

    data = request.json
    state_text = data.get('state', "")
    instructions = data.get('instructions', [])
    model_id = data.get('model_id', 'gpt')
    
    result = {}

    if model_id == 'gpt':
        # 1. GPT-4o-mini via OpenRouter
        start_time = time.time()
        gpt_response = ""
        gpt_cost = 0
        try:
            resp = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "openai/gpt-4o-mini",
                    "max_tokens": 100,
                    "messages": [
                        {"role": "system", "content": f"""You are a log analysis bot. Read the provided state carefully. Answer the following 3 YES/NO questions about the given state. You MUST answer in EXACTLY this JSON format and nothing else:
{{
  "q1": "YES/NO",
  "q2": "YES/NO",
  "q3": "YES/NO"
}}

Questions:
1. {instructions[0]}
2. {instructions[1]}
3. {instructions[2]}"""},
                        {"role": "user", "content": state_text}
                    ]
                }
            )
            resp_data = resp.json()
            gpt_time = time.time() - start_time
            if "choices" in resp_data:
                gpt_raw = resp_data["choices"][0]["message"]["content"]
                try:
                    js = json.loads(gpt_raw)
                    gpt_response = f"1. {js.get('q1')}<br>2. {js.get('q2')}<br>3. {js.get('q3')}"
                except:
                    gpt_response = f"<pre style='font-size:0.7em'>{gpt_raw}</pre>"
                tokens = resp_data.get("usage", {})
                prompt_tokens = tokens.get("prompt_tokens", 0)
                completion_tokens = tokens.get("completion_tokens", 0)
                # GPT-4o-mini pricing: $0.15/1M input, $0.60/1M output
                gpt_cost = (prompt_tokens * 0.150 / 1000000) + (completion_tokens * 0.600 / 1000000)
            else:
                gpt_response = "API Error: " + str(resp_data.get("error", resp_data))
        except Exception as e:
            gpt_time = time.time() - start_time
            gpt_response = f"Error: {str(e)}"

        cost_1m = gpt_cost * 1_000_000
        result = {
            "model": "GPT-4o-mini (OpenRouter)",
            "result": gpt_response,
            "latency_ms": round(gpt_time * 1000, 2),
            "cost": f"${gpt_cost:.6f} / request<br><span style='font-size:0.85em;color:#888'>(${(cost_1m):.2f} per 1M queries)</span>"
        }


    elif model_id == 'jev':
        # 2. Jev via OpenRouter Decisions API
        start_time = time.time()
        jev_response = ""
        jev_cost = 0
        try:
            resp = requests.post(
                "https://openrouter.ai/api/alpha/decisions",
                headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "typesafe/jev-1.13",
                    "state": state_text,
                    "questions": {
                        "question1": {
                            "type": "noul",
                            "instructions": instructions[0]
                        },
                        "question2": {
                            "type": "noul",
                            "instructions": instructions[1]
                        },
                        "question3": {
                            "type": "noul",
                            "instructions": instructions[2]
                        }
                    }
                }
            )
            resp_data = resp.json()
            jev_time = time.time() - start_time
            if "answers" in resp_data:
                ans1 = resp_data["answers"].get("question1", {})
                ans2 = resp_data["answers"].get("question2", {})
                ans3 = resp_data["answers"].get("question3", {})
                
                def fmt(prob): return f"Yes ({prob:.1f}%)" if prob > 50 else f"No ({100-prob:.1f}%)"
                
                jev_response = f"1. {fmt(ans1.get('noul', 0)*100)}<br>2. {fmt(ans2.get('noul', 0)*100)}<br>3. {fmt(ans3.get('noul', 0)*100)}"
                
                tokens = resp_data.get("usage", {})
                prompt_tokens = tokens.get("prompt_tokens")
                if not prompt_tokens:
                    # Fallback to estimate if missing
                    prompt_tokens = len(state_text + str(instructions)) // 4
                jev_cost = (prompt_tokens * 0.042 / 1000000)
            else:
                jev_response = "API Error: " + str(resp_data.get("error", resp_data))
        except Exception as e:
            jev_time = time.time() - start_time
            jev_response = f"Error: {str(e)}"

        cost_1m = jev_cost * 1_000_000
        result = {
            "model": "Jev Latest (OpenRouter)",
            "result": jev_response,
            "latency_ms": round(jev_time * 1000, 2),
            "cost": f"${jev_cost:.6f} / request<br><span style='font-size:0.85em;color:#888'>(${(cost_1m):.2f} per 1M queries)</span>"
        }

    elif model_id == 'laya':
        # 3. Laya locally
        start_time = time.time()
        laya_result_text = ""
        if laya_agent:
            try:
                res = laya_agent.predict(
                    state=state_text,
                    questions={
                        "question1": {
                            "type": "noul",
                            "instructions": instructions[0]
                        },
                        "question2": {
                            "type": "noul",
                            "instructions": instructions[1]
                        },
                        "question3": {
                            "type": "noul",
                            "instructions": instructions[2]
                        }
                    }
                )
                laya_time = time.time() - start_time
                ans1 = res.get("answers", {}).get("question1", {})
                ans2 = res.get("answers", {}).get("question2", {})
                ans3 = res.get("answers", {}).get("question3", {})
                
                def fmt(prob): return f"Yes ({prob:.1f}%)" if prob > 50 else f"No ({100-prob:.1f}%)"
                laya_result_text = f"1. {fmt(ans1.get('noul', 0)*100)}<br>2. {fmt(ans2.get('noul', 0)*100)}<br>3. {fmt(ans3.get('noul', 0)*100)}"
            except Exception as e:
                laya_time = time.time() - start_time
                laya_result_text = f"Error: {str(e)}"
        else:
            laya_time = 0
            laya_result_text = "Laya not loaded"
            
        result = {
            "model": "Laya (Local Engine)",
            "result": laya_result_text,
            "latency_ms": round(laya_time * 1000, 2),
            "cost": "$0.000000 / request<br><span style='font-size:0.85em;color:#10b981'>($0.00 per 1M queries)</span>"
        }

    return jsonify(result)

if __name__ == '__main__':
    print("Starting server... Navigate to http://localhost:5000 in your browser.")
    app.run(debug=True, port=5000)
