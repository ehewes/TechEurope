import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
from dotenv import load_dotenv
from aci import ACI

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize ACI client
aci = ACI()

try:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    aci_api_key = os.getenv("ACI_API_KEY")
    
    if not openai.api_key:
        raise ValueError("OPENAI_API_KEY not found in .env file")
    if not aci_api_key:
        print("Warning: ACI_API_KEY not found in .env file. ACI features will be limited.")
        
except ValueError as e:
    print(f"Error: {e}")


@app.route('/api/chat', methods=['POST'])
def chat_with_aci():
    """Enhanced chat endpoint that can use ACI.dev functions for SRE tasks"""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    message = data.get('message')
    linked_account_owner_id = data.get('linked_account_owner_id', 'default_user')

    if not message:
        return jsonify({"error": "Missing 'message' in request body"}), 400

    try:
        # Get available ACI functions for SRE tasks
        available_functions = []
        
        try:
            # Get GitHub functions that might be useful for SRE
            github_functions = [
                "GITHUB__GET_REPOSITORY",
                "GITHUB__LIST_REPOSITORY_COMMITS", 
                "GITHUB__GET_REPOSITORY_CONTENT",
                "GITHUB__CREATE_ISSUE",
                "GITHUB__LIST_ISSUES"
            ]
            
            for func_name in github_functions:
                try:
                    func_def = aci.functions.get_definition(func_name)
                    available_functions.append(func_def)
                except Exception as e:
                    print(f"Could not get function {func_name}: {e}")
                    
        except Exception as e:
            print(f"Error getting ACI functions: {e}")

        # Enhanced system prompt for SRE tasks
        system_prompt = """You are an expert SRE (Site Reliability Engineering) assistant with access to various tools. 
        You can help analyze deployment configurations, suggest improvements, create GitHub issues for tracking problems,
        and provide SRE best practices. 

        When analyzing configurations, focus on:
        1. Resource Management (CPU/memory limits)
        2. Security (exposed ports, privileges, secrets)
        3. Cost Optimization (resource sizing, unused resources)
        4. Monitoring and Observability
        5. High Availability and Disaster Recovery

        If you identify issues that need tracking, you can create GitHub issues.
        Always provide actionable recommendations."""

        # Prepare messages for OpenAI
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]

        # Make request to OpenAI with available tools
        if available_functions:
            response = openai.chat.completions.create(
                model="gpt-4o-2024-08-06",
                messages=messages,
                tools=available_functions,
                tool_choice="auto"
            )
        else:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages
            )

        assistant_message = response.choices[0].message
        
        # Handle tool calls if any
        if hasattr(assistant_message, 'tool_calls') and assistant_message.tool_calls:
            tool_results = []
            
            for tool_call in assistant_message.tool_calls:
                try:
                    result = aci.handle_function_call(
                        tool_call.function.name,
                        json.loads(tool_call.function.arguments),
                        linked_account_owner_id=linked_account_owner_id
                    )
                    tool_results.append({
                        "function": tool_call.function.name,
                        "result": result
                    })
                except Exception as e:
                    print(f"Error executing function {tool_call.function.name}: {e}")
                    tool_results.append({
                        "function": tool_call.function.name,
                        "error": str(e)
                    })
            
            # Get final response incorporating tool results
            if tool_results:
                followup_message = f"Based on the tool execution results: {json.dumps(tool_results, indent=2)}\n\nPlease provide a summary and any additional recommendations."
                
                final_response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages + [
                        {"role": "assistant", "content": assistant_message.content or ""},
                        {"role": "user", "content": followup_message}
                    ]
                )
                
                response_content = final_response.choices[0].message.content
            else:
                response_content = assistant_message.content
        else:
            response_content = assistant_message.content

        response_data = {
            "response": {
                "value": response_content,
                "annotations": []
            }
        }
        
        return jsonify(response_data)

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "Failed to get response from AI service."}), 500


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


@app.route('/api/create-issue', methods=['POST'])
def create_github_issue():
    """Create a GitHub issue for SRE problems"""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    repo_owner = data.get('repo_owner')
    repo_name = data.get('repo_name') 
    title = data.get('title')
    body = data.get('body')
    linked_account_owner_id = data.get('linked_account_owner_id', 'default_user')

    if not all([repo_owner, repo_name, title, body]):
        return jsonify({"error": "Missing required fields: repo_owner, repo_name, title, body"}), 400

    try:
        # Get the GitHub create issue function
        create_issue_function = aci.functions.get_definition("GITHUB__CREATE_ISSUE")
        
        # Execute the function via ACI
        result = aci.handle_function_call(
            "GITHUB__CREATE_ISSUE",
            {
                "owner": repo_owner,
                "repo": repo_name,
                "title": title,
                "body": body
            },
            linked_account_owner_id=linked_account_owner_id
        )
        
        return jsonify({
            "status": "success",
            "issue": result
        })

    except Exception as e:
        print(f"Error creating GitHub issue: {e}")
        return jsonify({"error": f"Failed to create GitHub issue: {str(e)}"}), 500


@app.route('/api/analyze-repo', methods=['POST'])
def analyze_repository():
    """Analyze a GitHub repository for SRE best practices"""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    repo_owner = data.get('repo_owner')
    repo_name = data.get('repo_name')
    linked_account_owner_id = data.get('linked_account_owner_id', 'default_user')

    if not all([repo_owner, repo_name]):
        return jsonify({"error": "Missing required fields: repo_owner, repo_name"}), 400

    try:
        # Get repository information
        repo_result = aci.handle_function_call(
            "GITHUB__GET_REPOSITORY",
            {
                "owner": repo_owner,
                "repo": repo_name
            },
            linked_account_owner_id=linked_account_owner_id
        )

        # Get repository contents (look for common config files)
        config_files = [
            "kubernetes.yaml", "k8s.yaml", "deployment.yaml", 
            "docker-compose.yml", "Dockerfile", ".github/workflows"
        ]
        
        file_contents = {}
        for file_path in config_files:
            try:
                content_result = aci.handle_function_call(
                    "GITHUB__GET_REPOSITORY_CONTENT",
                    {
                        "owner": repo_owner,
                        "repo": repo_name,
                        "path": file_path
                    },
                    linked_account_owner_id=linked_account_owner_id
                )
                file_contents[file_path] = content_result
            except:
                continue  # File doesn't exist, skip

        # Analyze with OpenAI
        analysis_prompt = f"""
        Analyze this GitHub repository for SRE best practices:
        
        Repository: {repo_owner}/{repo_name}
        Repository Info: {json.dumps(repo_result, indent=2)}
        
        Configuration Files Found: {json.dumps(file_contents, indent=2)}
        
        Please provide an SRE analysis covering:
        1. Infrastructure as Code practices
        2. CI/CD pipeline configuration
        3. Monitoring and observability setup
        4. Security configurations
        5. Cost optimization opportunities
        6. Recommended improvements
        """

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert SRE consultant analyzing repositories."},
                {"role": "user", "content": analysis_prompt}
            ]
        )

        return jsonify({
            "status": "success",
            "repository": repo_result,
            "analysis": response.choices[0].message.content,
            "config_files_found": list(file_contents.keys())
        })

    except Exception as e:
        print(f"Error analyzing repository: {e}")
        return jsonify({"error": f"Failed to analyze repository: {str(e)}"}), 500


@app.route('/')
def index():
    return "SRE Guardian Agent Running with ACI.dev Integration"


if __name__ == '__main__':
    app.run(debug=True, port=5001)