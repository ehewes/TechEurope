import json
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from aci import ACI
from aci.meta_functions import ACISearchFunctions
from aci.types.functions import FunctionDefinitionFormat
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Environment setup
LINKED_ACCOUNT_OWNER_ID = os.getenv("LINKED_ACCOUNT_OWNER_ID") or os.getenv("DEFAULT_LINKED_ACCOUNT_OWNER_ID", "")
if not LINKED_ACCOUNT_OWNER_ID:
    print("❌ Warning: No LINKED_ACCOUNT_OWNER_ID found in environment")
    print("Available env vars:", [k for k in os.environ.keys() if 'LINKED' in k.upper()])
    LINKED_ACCOUNT_OWNER_ID = "peopleagent"  # fallback default

# Initialize ACI and OpenAI clients
try:
    openai_client = OpenAI()  # gets OPENAI_API_KEY from environment
    print("✅ OpenAI client initialized")
except Exception as e:
    print(f"❌ OpenAI initialization failed: {e}")
    raise

try:
    aci = ACI()  # gets ACI_API_KEY from environment
    print("✅ ACI client initialized")
    ACI_ENABLED = True
except Exception as e:
    print(f"❌ ACI initialization failed: {e}")
    print("Running in fallback mode without ACI")
    aci = None
    ACI_ENABLED = False

# System prompt for the dynamic agent
SYSTEM_PROMPT = (
    "You are an expert SRE (Site Reliability Engineering) assistant with access to unlimited tools via ACI_SEARCH_FUNCTIONS. "
    "You can use ACI_SEARCH_FUNCTIONS to find relevant functions across all apps. "
    "Once you have identified the functions you need to use, you can append them to the tools list and use them in future tool calls. "
    
    "You can discover and use functions for ANY task: "
    "- GitHub operations (repositories, issues, commits, content, PRs) "
    "- Cloud services and infrastructure management "
    "- Configuration analysis and deployment reviews "
    "- Monitoring, logging, and observability "
    "- Security analysis and compliance checks "
    "- Cost optimization and resource management "
    "- CI/CD pipeline management "
    "- Database operations "
    "- Web search and research "
    "- And much more... "
    
    "IMPORTANT DEFAULTS: "
    "- For GitHub operations without specified repository, default to 'ehewes/TechEurope' "
    "- For create issue requests, extract title and description from user message "
    "- For list issues requests, format results clearly with issue details "
    "- For configuration analysis, provide detailed security and best practice recommendations "
    
    "Always provide actionable, expert-level SRE recommendations with clear explanations."
)

# ACI meta functions for dynamic function discovery
tools_meta = [
    ACISearchFunctions.to_json_schema(FunctionDefinitionFormat.OPENAI),
]


def execute_dynamic_agent(user_message, max_iterations=5):
    """
    Execute a dynamic agent conversation using ACI meta functions
    This replaces the main() function for Flask integration
    """
    if not ACI_ENABLED:
        return f"ACI is not available. Echo response: {user_message}"
    
    tools_retrieved = []
    chat_history = []
    
    try:
        for iteration in range(max_iterations):
            print(f"🔄 Agent iteration {iteration + 1}")
            
            # Make request to OpenAI with available tools
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ] + chat_history,
                tools=tools_meta + tools_retrieved,
                parallel_tool_calls=False,
            )

            # Process LLM response and potential function call
            assistant_message = response.choices[0].message
            content = assistant_message.content
            tool_call = (
                assistant_message.tool_calls[0]
                if assistant_message.tool_calls
                else None
            )
            
            if content:
                print(f"🤖 LLM Response: {content[:100]}...")
                chat_history.append({"role": "assistant", "content": content})

            # Handle function call if any
            if tool_call:
                print(f"🔧 Function Call: {tool_call.function.name}")
                print(f"📋 Arguments: {tool_call.function.arguments}")

                chat_history.append({"role": "assistant", "tool_calls": [tool_call]})
                
                try:
                    result = aci.handle_function_call(
                        tool_call.function.name,
                        json.loads(tool_call.function.arguments),
                        linked_account_owner_id=LINKED_ACCOUNT_OWNER_ID,
                        allowed_apps_only=True,
                        format=FunctionDefinitionFormat.OPENAI,
                    )
                    
                    # If searching functions, add them to tools_retrieved
                    if tool_call.function.name == ACISearchFunctions.get_name():
                        tools_retrieved.extend(result)
                        print(f"📚 Retrieved {len(result)} new functions")

                    print(f"✅ Function Result: {str(result)[:100]}...")
                    
                    # Continue loop, feeding the result back to the LLM for further instructions
                    chat_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result),
                    })
                    
                except Exception as e:
                    error_msg = f"Error executing function: {str(e)}"
                    print(f"❌ {error_msg}")
                    chat_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": error_msg,
                    })
            else:
                # If there's no further function call, exit the loop
                print("✅ Task Completed - No more function calls needed")
                break
        
        # Get the final response content
        final_content = "I apologize, but I encountered an issue processing your request."
        for message in reversed(chat_history):
            if message.get("role") == "assistant" and message.get("content"):
                final_content = message["content"]
                break
        
        return final_content
        
    except Exception as e:
        error_msg = f"Error in dynamic agent: {str(e)}"
        print(f"❌ {error_msg}")
        return f"I encountered an error processing your request: {str(e)}"


@app.route('/')
def index():
    return "🚀 SRE Guardian Agent - ACI Dynamic Function Discovery Enabled"


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Universal chat endpoint that handles all SRE tasks through dynamic agent
    Expects JSON with 'message' field and optional 'file_content' field
    """
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    message = data.get('message', '')
    file_content = data.get('file_content', '')

    if not message and not file_content:
        return jsonify({"error": "Missing 'message' or 'file_content' in request body"}), 400

    try:
        # Combine message and file content if both exist
        user_input = message
        if file_content:
            user_input += f"\n\nFile content to analyze:\n```\n{file_content}\n```"

        print(f"📨 Received request: {user_input[:100]}...")
        
        # Execute the dynamic agent
        response_content = execute_dynamic_agent(user_input)

        return jsonify({
            "response": {
                "value": response_content,
                "annotations": []
            }
        })

    except Exception as e:
        error_msg = f"Failed to get response from AI service: {str(e)}"
        print(f"❌ Chat endpoint error: {error_msg}")
        return jsonify({"error": error_msg}), 500


# Health check endpoint
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "service": "SRE Guardian Agent",
        "aci_enabled": True,
        "linked_account": LINKED_ACCOUNT_OWNER_ID
    })


if __name__ == '__main__':
    print("🚀 Starting SRE Guardian Agent with ACI Dynamic Function Discovery")
    app.run(debug=True, port=5001, host='127.0.0.1')
