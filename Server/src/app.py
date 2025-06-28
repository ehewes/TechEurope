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
    linked_account_owner_id = data.get('linked_account_owner_id', 'peopleagent')

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
    linked_account_owner_id = data.get('linked_account_owner_id', os.getenv('DEFAULT_LINKED_ACCOUNT_OWNER_ID', 'peopleagent'))

    if not all([repo_owner, repo_name, title, body]):
        return jsonify({"error": "Missing required fields: repo_owner, repo_name, title, body"}), 400

    try:
        # Get the GitHub create issue function
        create_issue_function = aci.functions.get_definition("GITHUB__CREATE_ISSUE")
        
        # Execute the function via ACI
        result = aci.handle_function_call(
            "GITHUB__CREATE_ISSUE",
            {
                "body": {
                    "title": title,
                    "body": body,
                    "labels": ["enhancement"],
                    "assignees": []
                },
                "path": {
                    "repo": repo_name,
                    "owner": repo_owner
                }
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
    linked_account_owner_id = data.get('linked_account_owner_id', os.getenv('DEFAULT_LINKED_ACCOUNT_OWNER_ID', 'peopleagent'))

    if not all([repo_owner, repo_name]):
        return jsonify({"error": "Missing required fields: repo_owner, repo_name"}), 400

    try:
        # Get repository information
        repo_result = aci.handle_function_call(
            "GITHUB__GET_REPOSITORY",
            {
                "path": {
                    "repo": repo_name,
                    "owner": repo_owner
                }
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


@app.route('/api/filter-request', methods=['POST'])
def filter_request():
    """Intelligent request filtering endpoint that determines which backend function to call"""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    message = data.get('message')
    has_file = data.get('has_file', False)
    file_type = data.get('file_type', '')
    file_content = data.get('file_content', '')

    if not message:
        return jsonify({"error": "Missing 'message' in request body"}), 400

    try:
        # Enhanced system prompt for request classification
        system_prompt = """You are an intelligent request router for an SRE agent. Analyze user requests and determine which function to call.

Available Functions:
1. "chat" - General SRE questions, GitHub operations, complex tasks
2. "config-analysis" - Analyze YAML/JSON configuration files  
3. "repo-analysis" - Analyze specific GitHub repositories
4. "create-issue" - Create GitHub issues
5. "list-issues" - List GitHub issues from repositories

Classification Rules:
- Has file upload (YAML/JSON) OR mentions "config" OR "configuration" → "config-analysis"
- Mentions specific repo like "owner/repo" OR "analyze repository" OR "analyze repo" → "repo-analysis"  
- Mentions "create issue" OR "file bug" OR "track problem" OR "create an issue" OR "file an issue" OR "report this" OR "log this issue" → "create-issue"
- Mentions "list issues" OR "show issues" OR "get issues" OR "what issues" OR "view issues" OR "issues in" OR "issues from" → "list-issues"
- Everything else → "chat"

Pay special attention to patterns:
create-issue:
- "create an issue on [repo] saying [description]"
- "file a bug for [component/repo]"
- "track this in [repo]"
- "report this problem"
- "log this as an issue"

list-issues:
- "list issues from [repo]"
- "show me issues in [repo]"
- "what issues are open in [repo]"
- "get issues for [repo]"
- "view issues from [repo]"

CRITICAL: Respond with ONLY valid JSON. No other text.

Example response:
{
    "function": "create-issue",
    "confidence": 0.9,
    "reasoning": "User wants to create an issue",
    "extracted_params": {}
}"""

        # Prepare the analysis prompt
        analysis_prompt = f"""User Message: "{message}"
File Upload: {has_file}
File Type: {file_type}

Classify this request and return JSON only."""

        # Use GPT-4o for intelligent classification
        response = openai.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": analysis_prompt}
            ],
            temperature=0.1,  # Low temperature for consistent classification
            response_format={"type": "json_object"}  # Force JSON output
        )

        # Parse the response
        response_text = response.choices[0].message.content.strip()
        print(f"Raw GPT response: {response_text}")  # Debug logging
        
        classification_result = json.loads(response_text)
        
        # Enhanced parameter extraction for repo-analysis and create-issue functions
        if classification_result.get("function") in ["repo-analysis", "create-issue", "list-issues"]:
            extracted_params = extract_parameters_from_message(message, classification_result.get("function"))
            classification_result["extracted_params"] = extracted_params
        
        return jsonify({
            "status": "success",
            "classification": classification_result
        })

    except json.JSONDecodeError as e:
        print(f"Error parsing classification result: {e}")
        # Fallback to general chat
        return jsonify({
            "status": "success", 
            "classification": {
                "function": "chat",
                "confidence": 0.5,
                "reasoning": "Fallback due to parsing error",
                "extracted_params": {}
            }
        })
    except Exception as e:
        print(f"Error in request filtering: {e}")
        return jsonify({"error": f"Failed to classify request: {str(e)}"}), 500


@app.route('/api/execute-function', methods=['POST'])
def execute_function():
    """Execute the determined function based on classification"""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    function_name = data.get('function')
    message = data.get('message')
    params = data.get('params', {})
    file_content = data.get('file_content')
    
    if not function_name or not message:
        return jsonify({"error": "Missing 'function' or 'message' in request body"}), 400

    try:
        if function_name == "config-analysis":
            # Use file content or message for config analysis
            config_to_analyze = file_content if file_content else message
            return execute_config_analysis(config_to_analyze)
            
        elif function_name == "repo-analysis":
            # Extract repo details and call repo analysis
            repo_owner = params.get('repo_owner')
            repo_name = params.get('repo_name')
            
            # Default repo_owner to 'ehewes' if not provided but repo_name is present
            if repo_name and not repo_owner:
                repo_owner = "ehewes"
            
            # Default both repo_owner and repo_name if neither is specified
            if not repo_owner and not repo_name:
                repo_owner = "ehewes"
                repo_name = "TechEurope"
            
            if not repo_owner or not repo_name:
                # Try to provide helpful feedback
                if not repo_owner:
                    error_msg = f"Found repository '{repo_name}' but could not determine the owner. Please specify like 'owner/{repo_name}'"
                else:
                    error_msg = f"Found owner '{repo_owner}' but could not determine the repository name. Please specify like '{repo_owner}/repository-name'"
                
                return jsonify({
                    "error": error_msg,
                    "suggestion": "Try rephrasing your request like: 'analyze owner/repo' or 'analyze the TechEurope repository'",
                    "extracted_params": params
                }), 400
                
            return execute_repo_analysis(repo_owner, repo_name, os.getenv('DEFAULT_LINKED_ACCOUNT_OWNER_ID', 'peopleagent'))
            
        elif function_name == "create-issue":
            # Extract issue details and create GitHub issue
            repo_owner = params.get('repo_owner')
            repo_name = params.get('repo_name')
            title = params.get('title', message.split('\n')[0] if message else 'Issue from AI Agent')
            body = params.get('body', message)
            
            # Default repo_owner to 'ehewes' if not provided but repo_name is present
            if repo_name and not repo_owner:
                repo_owner = "ehewes"
            
            # Default both repo_owner and repo_name if neither is specified
            if not repo_owner and not repo_name:
                repo_owner = "ehewes"
                repo_name = "TechEurope"
            
            # Better error handling with helpful messages (only if truly missing after defaults)
            if not repo_owner or not repo_name:
                # Try to provide helpful feedback
                if not repo_owner:
                    error_msg = f"Found repository '{repo_name}' but could not determine the owner. Please specify like 'owner/{repo_name}'"
                else:
                    error_msg = f"Found owner '{repo_owner}' but could not determine the repository name. Please specify like '{repo_owner}/repository-name'"
                
                return jsonify({
                    "error": error_msg,
                    "suggestion": "Try rephrasing your request like: 'create an issue on owner/repo saying we need to fix the authentication bug'",
                    "extracted_params": params
                }), 400
                
            return execute_create_issue(repo_owner, repo_name, title, body, os.getenv('DEFAULT_LINKED_ACCOUNT_OWNER_ID', 'peopleagent'))
            
        elif function_name == "list-issues":
            # Extract repo details and list GitHub issues
            repo_owner = params.get('repo_owner')
            repo_name = params.get('repo_name')
            
            # Default repo_owner to 'ehewes' if not provided but repo_name is present
            if repo_name and not repo_owner:
                repo_owner = "ehewes"
            
            # Default both repo_owner and repo_name if neither is specified
            if not repo_owner and not repo_name:
                repo_owner = "ehewes"
                repo_name = "TechEurope"
            
            if not repo_owner or not repo_name:
                # Try to provide helpful feedback
                if not repo_owner:
                    error_msg = f"Found repository '{repo_name}' but could not determine the owner. Please specify like 'owner/{repo_name}'"
                else:
                    error_msg = f"Found owner '{repo_owner}' but could not determine the repository name. Please specify like '{repo_owner}/repository-name'"
                
                return jsonify({
                    "error": error_msg,
                    "suggestion": "Try rephrasing your request like: 'list issues from owner/repo' or 'show me issues in TechEurope'",
                    "extracted_params": params
                }), 400
                
            return execute_list_issues(repo_owner, repo_name, os.getenv('DEFAULT_LINKED_ACCOUNT_OWNER_ID', 'peopleagent'))
            
        elif function_name == "chat":
            # Call the enhanced chat endpoint
            return execute_chat_function(message, os.getenv('DEFAULT_LINKED_ACCOUNT_OWNER_ID', 'peopleagent'))
            
        else:
            return jsonify({"error": f"Unknown function: {function_name}"}), 400

    except Exception as e:
        print(f"Error executing function {function_name}: {e}")
        return jsonify({"error": f"Failed to execute function: {str(e)}"}), 500


def execute_config_analysis(config_content):
    """Execute config analysis function logic"""
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
        Configuration:
        {config_content}
        """

        chat_completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful SRE assistant."},
                {"role": "user", "content": prompt},
            ]
        )

        analysis_result = chat_completion.choices[0].message.content

        return jsonify({
            "response": {
                "value": analysis_result.strip(),
                "annotations": []
            }
        })

    except Exception as e:
        print(f"Config analysis error: {e}")
        return jsonify({"error": "Failed to get analysis from AI service."}), 500


def execute_repo_analysis(repo_owner, repo_name, linked_account_owner_id):
    """Execute repository analysis function logic"""
    try:
        # Get repository information
        repo_result = aci.handle_function_call(
            "GITHUB__GET_REPOSITORY",
            {
                "path": {
                    "repo": repo_name,
                    "owner": repo_owner
                }
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
            "response": {
                "value": response.choices[0].message.content,
                "annotations": []
            },
            "repository": repo_result,
            "config_files_found": list(file_contents.keys())
        })

    except Exception as e:
        print(f"Repo analysis error: {e}")
        return jsonify({"error": f"Failed to analyze repository: {str(e)}"}), 500


def execute_create_issue(repo_owner, repo_name, title, body, linked_account_owner_id):
    """Execute GitHub issue creation function logic"""
    try:
        # Execute the function via ACI
        result = aci.handle_function_call(
            "GITHUB__CREATE_ISSUE",
            {
                "body": {
                    "title": title,
                    "body": body,
                    "labels": ["enhancement"],
                    "assignees": []
                },
                "path": {
                    "repo": repo_name,
                    "owner": repo_owner
                }
            },
            linked_account_owner_id=linked_account_owner_id
        )
        
        return jsonify({
            "response": {
                "value": f"✅ **GitHub Issue Created Successfully!**\n\n**Repository:** {repo_owner}/{repo_name}\n**Title:** {title}\n**Issue URL:** {result.get('html_url', 'N/A')}\n\nThe issue has been created and is now ready for tracking and resolution.",
                "annotations": []
            },
            "issue": result
        })

    except Exception as e:
        print(f"Issue creation error: {e}")
        return jsonify({"error": f"Failed to create GitHub issue: {str(e)}"}), 500


def execute_chat_function(message, linked_account_owner_id):
    """Execute chat function logic"""
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

        return jsonify({
            "response": {
                "value": response_content,
                "annotations": []
            }
        })

    except Exception as e:
        print(f"Chat function error: {e}")
        return jsonify({"error": "Failed to get response from AI service."}), 500


@app.route('/')
def index():
    return "SRE Guardian Agent Running with ACI.dev Integration"


def extract_parameters_from_message(message, function_type):
    """Enhanced parameter extraction using GPT-4o to parse natural language"""
    import re
    
    # Initialize parameters
    params = {}
    
    try:
        if function_type == "repo-analysis":
            # Look for explicit repo patterns first
            repo_pattern = r'([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+)'
            repo_match = re.search(repo_pattern, message)
            if repo_match:
                owner, repo = repo_match.group(1).split('/')
                params = {"repo_owner": owner, "repo_name": repo}
            else:
                # Use GPT-4o to extract repo information from natural language
                extraction_prompt = f"""Extract GitHub repository information from this message: "{message}"

Return only JSON with repo_owner and repo_name. If not found, return empty values.
Example: {{"repo_owner": "microsoft", "repo_name": "vscode"}}"""

                response = openai.chat.completions.create(
                    model="gpt-4o-2024-08-06",
                    messages=[{"role": "user", "content": extraction_prompt}],
                    temperature=0.1,
                    response_format={"type": "json_object"}
                )
                
                extracted = json.loads(response.choices[0].message.content.strip())
                params = {
                    "repo_owner": extracted.get("repo_owner", ""),
                    "repo_name": extracted.get("repo_name", "")
                }
        elif function_type == "list-issues":
            # First try regex patterns for explicit owner/repo format
            repo_pattern = r'([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+)'
            repo_match = re.search(repo_pattern, message)
            
            if repo_match:
                owner, repo = repo_match.group(1).split('/')
                params = {
                    "repo_owner": owner,
                    "repo_name": repo
                }
            else:
                # Use GPT-4o to extract repository information from natural language
                extraction_prompt = f"""Extract GitHub repository information from this list issues request: "{message}"

Examples of what to extract:
- "list issues from TechEurope" → repo_owner: "ehewes", repo_name: "TechEurope"
- "show me issues in my-project" → repo_name: "my-project", repo_owner: "" (to be defaulted)
- "what issues are open in user/repository" → repo_owner: "user", repo_name: "repository"
- "get issues for the main repo" → try to infer from context

Return JSON with repo_owner and repo_name. If repo_owner not specified, leave empty (will default to "ehewes").

Message: "{message}"

Return only JSON:"""

                response = openai.chat.completions.create(
                    model="gpt-4o-2024-08-06",
                    messages=[{"role": "user", "content": extraction_prompt}],
                    temperature=0.1,
                    response_format={"type": "json_object"}
                )
                
                extracted = json.loads(response.choices[0].message.content.strip())
                params = {
                    "repo_owner": extracted.get("repo_owner", ""),
                    "repo_name": extracted.get("repo_name", "")
                }
        elif function_type == "create-issue":
            # First try regex patterns
            repo_pattern = r'([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+)'
            repo_match = re.search(repo_pattern, message)
            
            if repo_match:
                owner, repo = repo_match.group(1).split('/')
                params = {
                    "repo_owner": owner,
                    "repo_name": repo,
                    "title": message.split('\n')[0] if '\n' in message else message[:100],
                    "body": message
                }
            else:
                # Use GPT-4o to extract issue parameters from natural language
                extraction_prompt = f"""Extract GitHub issue information from this natural language request: "{message}"

Examples of what to extract:
- "create an issue on TechEurope saying we need new features" → repo_owner: "ehewes", repo_name: "TechEurope", title: "We need new features", body: original message
- "file a bug report for the authentication module" → title about authentication bug, body with details
- "track this problem in our main repository" → extract repo and issue details

Return JSON with repo_owner, repo_name, title, and body. Make title concise and body descriptive.
If repo not specified, try to infer from context or leave empty.

Message: "{message}"

Return only JSON:"""

                response = openai.chat.completions.create(
                    model="gpt-4o-2024-08-06",
                    messages=[{"role": "user", "content": extraction_prompt}],
                    temperature=0.1,
                    response_format={"type": "json_object"}
                )
                
                extracted = json.loads(response.choices[0].message.content.strip())
                params = {
                    "repo_owner": extracted.get("repo_owner", ""),
                    "repo_name": extracted.get("repo_name", ""),
                    "title": extracted.get("title", message[:100]),
                    "body": extracted.get("body", message)
                }
                
                # Default to TechEurope repo if no repo is specified at all
                if not params.get("repo_name") and not params.get("repo_owner"):
                    params["repo_name"] = "TechEurope"
                    params["repo_owner"] = "ehewes"
    except Exception as e:
        print(f"Error in parameter extraction: {e}")
        # Fallback to simple regex extraction
        repo_pattern = r'([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+)'
        repo_match = re.search(repo_pattern, message)
        if repo_match:
            owner, repo = repo_match.group(1).split('/')
            params = {"repo_owner": owner, "repo_name": repo}
            if function_type == "create-issue":
                params.update({
                    "title": message.split('\n')[0] if '\n' in message else message[:100],
                    "body": message
                })
        else:
            # If no repo pattern found and it's create-issue, default to TechEurope
            if function_type == "create-issue":
                params = {
                    "repo_owner": "ehewes",
                    "repo_name": "TechEurope", 
                    "title": message.split('\n')[0] if '\n' in message else message[:100],
                    "body": message
                }
    
    # Force repo_owner to 'ehewes' if missing and repo_name is present
    if params.get("repo_name") and not params.get("repo_owner"):
        params["repo_owner"] = "ehewes"
    return params


@app.route('/api/list-issues', methods=['POST'])
def list_github_issues():
    """List GitHub issues for a repository"""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    repo_owner = data.get('repo_owner')
    repo_name = data.get('repo_name')
    linked_account_owner_id = data.get('linked_account_owner_id', os.getenv('DEFAULT_LINKED_ACCOUNT_OWNER_ID', 'peopleagent'))

    # Default repo_owner to 'ehewes' if not provided but repo_name is present
    if repo_name and not repo_owner:
        repo_owner = "ehewes"

    if not all([repo_owner, repo_name]):
        return jsonify({"error": "Missing required fields: repo_owner, repo_name"}), 400

    try:
        # Execute the GITHUB__LIST_ISSUES function via ACI
        result = aci.handle_function_call(
            "GITHUB__LIST_ISSUES",
            {
                "path": {
                    "repo": repo_name,
                    "owner": repo_owner
                }
            },
            linked_account_owner_id=linked_account_owner_id
        )
        
        return jsonify({
            "status": "success",
            "repository": f"{repo_owner}/{repo_name}",
            "issues": result
        })

    except Exception as e:
        print(f"Error listing GitHub issues: {e}")
        return jsonify({"error": f"Failed to list GitHub issues: {str(e)}"}), 500


def execute_list_issues(repo_owner, repo_name, linked_account_owner_id):
    """Execute GitHub list issues function logic"""
    try:
        # Execute the function via ACI
        result = aci.handle_function_call(
            "GITHUB__LIST_ISSUES",
            {
                "path": {
                    "repo": repo_name,
                    "owner": repo_owner
                }
            },
            linked_account_owner_id=linked_account_owner_id
        )
        
        # Format the response for display
        issues_data = result.get('data', []) if isinstance(result, dict) else result
        issues_count = len(issues_data) if isinstance(issues_data, list) else 0
        
        # Create formatted markdown response with meaningful issue details
        if issues_count == 0:
            formatted_response = f"📋 **GitHub Issues for {repo_owner}/{repo_name}**\n\n✅ **No open issues found!** This repository is in great shape.\n\n---\n*Repository appears to be well-maintained with no outstanding issues.*"
        else:
            formatted_response = f"📋 **GitHub Issues for {repo_owner}/{repo_name}**\n\n**Total Issues:** {issues_count} open\n\n"
            
            for i, issue in enumerate(issues_data, 1):
                # Extract key information from each issue
                issue_number = issue.get('number', 'N/A')
                title = issue.get('title', 'No title')
                state = issue.get('state', 'unknown')
                created_at = issue.get('created_at', '')
                author = issue.get('user', {}).get('login', 'unknown')
                html_url = issue.get('html_url', '')
                body = issue.get('body', '')
                labels = issue.get('labels', [])
                comments_count = issue.get('comments', 0)
                
                # Format creation date
                if created_at:
                    try:
                        from datetime import datetime
                        created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        created_str = created_date.strftime('%Y-%m-%d')
                    except:
                        created_str = created_at[:10]
                else:
                    created_str = 'Unknown'
                
                # Format labels
                label_names = [label.get('name', '') for label in labels if label.get('name')]
                labels_str = ', '.join(label_names) if label_names else 'none'
                
                # Create issue summary
                formatted_response += f"### Issue #{issue_number}: {title}\n"
                formatted_response += f"- **Status:** {state.title()}\n"
                formatted_response += f"- **Author:** {author}\n"
                formatted_response += f"- **Created:** {created_str}\n"
                formatted_response += f"- **Labels:** {labels_str}\n"
                formatted_response += f"- **Comments:** {comments_count}\n"
                
                if body and body.strip():
                    # Truncate body if too long
                    body_preview = body[:200] + "..." if len(body) > 200 else body
                    formatted_response += f"- **Description:** {body_preview}\n"
                
                formatted_response += f"- **Link:** [View Issue]({html_url})\n\n"
            
            # Add summary at the end
            formatted_response += "---\n"
            formatted_response += f"💡 **Summary:** Found {issues_count} open issue{'s' if issues_count != 1 else ''} that may need attention.\n"
            formatted_response += f"🔗 **Repository:** [{repo_owner}/{repo_name}](https://github.com/{repo_owner}/{repo_name}/issues)"
        
        return jsonify({
            "response": {
                "value": formatted_response,
                "annotations": []
            },
            "repository": f"{repo_owner}/{repo_name}",
            "issues": result,
            "count": issues_count
        })

    except Exception as e:
        print(f"List issues error: {e}")
        return jsonify({"error": f"Failed to list GitHub issues: {str(e)}"}), 500