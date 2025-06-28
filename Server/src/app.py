import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

try:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        raise ValueError("OPENAI_API_KEY not found in .env file")
except ValueError as e:
    print(f"Error: {e}")


@app.route('/check-config', methods=['POST'])
def check_config_endpoint():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    config_yaml = data.get('config')

    if not config_yaml:
        return jsonify({"error": "Missing 'config' in request body"}), 400

    try:
        prompt = f"""
        You are an expert SRE and security engineer reviewing a deployment configuration.
        Analyze the following YAML for critical issues. Focus on these areas:
        1.  **Resource Management:** Missing 'resources.requests' or 'resources.limits' for CPU/memory.
        2.  **Security:** Insecurely exposed ports, use of privileged mode, or running as root user.
        3.  **Best Practices:** Use of the ':latest' image tag.
        4.  **Cost Optimisation:** Identify resources defined in this YAML that will incur costs (e.g., Load Balancers, Persistent Volumes, public IPs). 
            *Provide a high-level cost considerations for these resources. 
            *Offer specific, actionable recommendations to reduce costs where possible.

       **Report Format:**
       Please format your response using Markdown with a main heading for each of the four areas.
       If no issues are found in a specific area, state that "No issues found."
       You may assume the cloud provider is AWS unless specified otherwise, but you must state this assumption in your cost analysis.

        ---
        YAML Configuration:
        {config_yaml}
        """

        chat_completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful SRE assistant."},
                {"role": "user", "content": prompt},
            ]
        )

        analysis_result = chat_completion.choices[0].message.content

        response_data = {
            "status": "success",
            "report": analysis_result.strip()
        }
        return jsonify(response_data)

    except Exception as e:
        print(f"An error occurred calling OpenAI: {e}")
        return jsonify({"error": "Failed to get analysis from AI service."}), 500


@app.route('/')
def index():
    return "SRE Agent Running."


if __name__ == '__main__':
    app.run(debug=True, port=5001)