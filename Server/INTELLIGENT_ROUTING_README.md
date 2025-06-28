# ACI.dev SRE Agent with Intelligent Routing

This project integrates **ACI.dev** (AI-powered SRE agent) with a Flask backend and React frontend to provide intelligent routing of user requests to the appropriate backend functions.

## 🚀 Features

### Intelligent Request Classification
The system uses **GPT-4o** to analyze user requests and automatically route them to the correct backend function:

- **💬 Chat** - General SRE conversations, advice, best practices
- **🔍 Config Analysis** - Analyze YAML/JSON deployment configurations 
- **📊 Repository Analysis** - Analyze GitHub repositories for SRE best practices
- **🎫 GitHub Issues** - Create GitHub issues for tracking problems

### Smart Detection Examples

| User Input | Function | Why |
|------------|----------|-----|
| "What are Kubernetes best practices?" | `chat` | General SRE question |
| "Analyze repository microsoft/vscode" | `repo-analysis` | Contains repo reference |
| "Create issue in facebook/react for docs" | `create-issue` | Intent to create GitHub issue |
| Upload YAML/JSON file | `config-analysis` | File upload detected |

## 🏗️ Architecture

```
Frontend (React) 
    ↓ User Request + File
Backend (Flask)
    ↓ 1. Classify Request (/api/filter-request)
GPT-4o Model
    ↓ Classification Result
Backend (Flask)
    ↓ 2. Execute Function (/api/execute-function)
ACI.dev + OpenAI
    ↓ Response
Frontend (React)
```

## 📡 API Endpoints

### `/api/filter-request` (POST)
Classifies user requests using GPT-4o.

**Request:**
```json
{
  "message": "Analyze repository owner/repo",
  "has_file": false,
  "file_type": ""
}
```

**Response:**
```json
{
  "function": "repo-analysis",
  "confidence": 0.95,
  "reasoning": "User wants to analyze a GitHub repository",
  "parameters": {
    "repo_owner": "owner",
    "repo_name": "repo"
  }
}
```

### `/api/execute-function` (POST)
Executes the classified function with extracted parameters.

**Request:**
```json
{
  "function": "repo-analysis", 
  "parameters": {"repo_owner": "owner", "repo_name": "repo"},
  "message": "Analyze repository owner/repo",
  "file_content": null,
  "linked_account_owner_id": "user_id"
}
```

## 🛠️ Setup Instructions

### 1. Backend Setup

1. **Install dependencies:**
   ```bash
   cd Server
   pip install -r requirements.txt
   ```

2. **Environment variables:**
   Copy `.env.example` to `.env` and add your API keys:
   ```bash
   OPENAI_API_KEY=your_openai_api_key
   ACI_API_KEY=your_aci_api_key
   ```

3. **Run the Flask server:**
   ```bash
   cd src
   python app.py
   ```
   Server runs on `http://localhost:5001`

### 2. Frontend Setup

1. **Install dependencies:**
   ```bash
   cd Website/ReactBoiler-Temp
   npm install
   ```

2. **Run the React app:**
   ```bash
   npm run dev
   ```
   App runs on `http://localhost:3000`

## 🧪 Testing

Run the intelligent routing test script:

```bash
cd Server
python test_intelligent_routing.py
```

This script tests:
- Request classification accuracy
- Parameter extraction 
- Function routing
- Error handling

## 📝 Configuration Analysis

Upload YAML/JSON files for comprehensive SRE analysis:

### ✅ What it checks:
- **Resource Management**: CPU/memory limits and requests
- **Security**: Privileged containers, root users, exposed ports
- **Cost Optimization**: Load balancers, storage, resource sizing
- **Best Practices**: Image tags, readiness probes, labels

### 📊 Sample Analysis Output:
```markdown
# Resource Management
❌ Missing resource requests and limits for container 'nginx'

# Security
⚠️ Container running as root user (runAsUser: 0)
⚠️ Privileged mode enabled 

# Cost Optimization  
💰 LoadBalancer service will incur AWS costs (~$20/month)
💰 100Gi PVC will cost ~$10/month in AWS EBS

# Recommendations
1. Add resource limits: cpu: 100m, memory: 128Mi
2. Use non-root user: runAsUser: 1000
3. Consider NodePort instead of LoadBalancer for internal services
```

## 🔧 Advanced Features

### GitHub Integration
- **Repository Analysis**: Automatically scans repos for SRE best practices
- **Issue Creation**: Creates detailed GitHub issues with SRE context
- **Commit Analysis**: Reviews recent changes for reliability issues

### ACI.dev Functions
The system leverages ACI.dev's powerful function library:
- `GITHUB__GET_REPOSITORY` - Repository metadata
- `GITHUB__GET_REPOSITORY_CONTENT` - File content analysis  
- `GITHUB__CREATE_ISSUE` - Issue creation
- `GITHUB__LIST_ISSUES` - Issue tracking

## 🎯 Use Cases

1. **Configuration Review**: Upload Kubernetes YAML for instant SRE analysis
2. **Repository Auditing**: Analyze any public GitHub repo for SRE compliance
3. **Issue Tracking**: Create detailed GitHub issues for SRE improvements
4. **SRE Consultation**: Get expert advice on deployment strategies

## 🚨 Error Handling

The system includes robust error handling:
- Classification fallback to `chat` function
- Graceful degradation when APIs are unavailable  
- User-friendly error messages
- Automatic retry logic for transient failures

## 🔮 Future Enhancements

- [ ] Support for more file types (Dockerfiles, Terraform)
- [ ] Integration with more version control systems
- [ ] Real-time collaboration features
- [ ] Advanced cost modeling and predictions
- [ ] Custom SRE rule sets and policies

## 📚 Dependencies

### Backend
- `flask` - Web framework
- `openai` - GPT-4o integration  
- `aci-sdk-1.0.0b2` - ACI.dev integration
- `python-dotenv` - Environment management
- `flask-cors` - CORS handling

### Frontend  
- `react` - UI framework
- `@nextui-org/react` - UI components
- `lucide-react` - Icons
- `react-markdown` - Markdown rendering

---

**Built with ❤️ using ACI.dev and OpenAI**
