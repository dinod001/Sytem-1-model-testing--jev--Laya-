# 🚀 System 1 vs Auto-Regressive LLM Benchmark Lab

Welcome to the **Model Performance Lab**! This project is a beautifully designed, real-time benchmark tool that compares the latency, cost, and accuracy of traditional Auto-Regressive LLMs (like GPT-4o-mini) against the new generation of **System 1 Decision Models** (like Jev and Laya). 

System 1 models bypass token generation entirely, delivering **O(1) time complexity** for decision-making, routing, classification, and guardrails.

## 🌟 Why this exists?

When evaluating complex states (like long customer support emails) for multiple criteria (e.g., routing to legal, identifying data leaks, enforcing guardrails), traditional LLMs must output JSON objects token-by-token. This drastically increases both generation latency and output token cost. 

This lab proves that System 1 models:
- 🏎️ Are **~1.6x faster** by evaluating multiple parallel questions in a single forward pass.
- 💰 Are **~6x cheaper** per 1M queries (because there is 0 output token cost).
- 🧠 Deliver highly accurate, un-hallucinated probabilities instead of fragile text JSONs.

---

## 🛠️ Setup Instructions

### 1. Prerequisites
- Python 3.9+
- An [OpenRouter API Key](https://openrouter.ai/) for cloud benchmarks

### 2. Installation
Clone the repository and set up a virtual environment:

```bash
git clone <your-repo-url>
cd jev-benchmark
python -m venv .venv
```

Activate the virtual environment:
- **Windows:** `.venv\Scripts\activate`
- **Mac/Linux:** `source .venv/bin/activate`

Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory and add your OpenRouter API key:
```env
OPENROUTER_API_KEY=your_api_key_here
```

### 4. Run the Server
Start the Flask application:
```bash
python app.py
```
Then navigate to `http://localhost:5000` in your web browser.

---

## 📊 Benchmark Breakdown

| Model | Architecture | Speed (Avg) | Cost (per 1M queries) | Ideal Use Case |
|-------|-------------|-------------|----------------------|----------------|
| **GPT-4o-mini** | Auto-Regressive | 🐢 ~4.3s | 💵 ~$57.00 | Open-ended text generation, chat |
| **Jev Latest** | System 1 (Cloud) | 🚀 ~2.6s | 🪙 ~$9.20 | Cloud routing, JSON classification |
| **Laya** | System 1 (Local) | 🖥️ CPU Bound| 🆓 $0.00 | On-device, edge processing, zero-cost routing |

*Note: The speed advantage of System 1 models scales drastically as the number of parallel questions increases. While an LLM takes longer to type out a massive JSON, Jev/Laya evaluate 100 questions in the same time it takes to evaluate 1.*

## 🧪 Testing Methodology
The UI provides a massive, multi-faceted customer email thread. You can configure up to 3 distinct evaluation statements simultaneously. When you click **Run Benchmark**, the app fires concurrent requests to the models and tracks the **Time to First Token (TTFT)** and absolute response times using a GitHub-style timeline visualizer. 

*I've locally tested this extensively to validate the marketing claims of System 1 architecture.*
