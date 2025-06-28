# 🧪 Frontend Testing Guide - ACI.dev SRE Agent

## 🚀 Quick Start Testing

Your React frontend is now running at: **http://localhost:5174**
Your Flask backend is running at: **http://localhost:5001**

## 📋 Test Scenarios

### 1. 💬 **General SRE Chat** 
**Try these messages:**
```
What are the best practices for Kubernetes resource management?
How do I implement monitoring in a microservices architecture?
Explain the difference between horizontal and vertical scaling
```
**Expected:** Should show 💬 emoji and route to enhanced chat with ACI.dev functions

---

### 2. 🔍 **Configuration Analysis**
**Upload a YAML/JSON file or try:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: test-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: test-app
  template:
    metadata:
      labels:
        app: test-app
    spec:
      containers:
      - name: test-app
        image: nginx:latest
        ports:
        - containerPort: 80
        securityContext:
          runAsUser: 0
          privileged: true
```
**Expected:** Should show 🔍 emoji and provide detailed SRE analysis

---

### 3. 📊 **Repository Analysis**
**Try these messages:**
```
Analyze the GitHub repository microsoft/vscode for SRE practices
Please review kubernetes/kubernetes for deployment best practices
Check facebook/react repository for monitoring setup
```
**Expected:** Should show 📊 emoji and extract repository information

---

### 4. 🎫 **GitHub Issue Creation**
**Try these messages:**
```
Create a GitHub issue in microsoft/vscode about missing deployment docs
File a bug report in kubernetes/kubernetes for pod scheduling issues
Track an issue in facebook/react for performance monitoring
```
**Expected:** Should show 🎫 emoji and extract repository and issue details

---

## 🎯 Testing Checklist

### ✅ **Visual Indicators**
- [ ] Messages show appropriate emoji (💬🔍📊🎫)
- [ ] File upload works for YAML/JSON files
- [ ] Response formatting uses Markdown
- [ ] Loading spinner appears during processing
- [ ] Error messages are user-friendly

### ✅ **Intelligent Routing**
- [ ] General questions → Chat function
- [ ] File uploads → Config analysis
- [ ] "Analyze repo owner/name" → Repository analysis
- [ ] "Create issue" → GitHub issue creation
- [ ] Repository names extracted correctly (e.g., microsoft/vscode)

### ✅ **Backend Integration**
- [ ] Classification endpoint responding correctly
- [ ] Execution endpoint processing requests
- [ ] File content passed to backend properly
- [ ] Error handling for missing API keys

## 🐛 Troubleshooting

### **Common Issues:**

1. **CORS Errors**
   - Flask server includes CORS headers
   - Check browser console for detailed errors

2. **Classification Fallback**
   - If requests always route to "chat", check OpenAI API key
   - Verify GPT-4o model access in your OpenAI account

3. **ACI.dev Functions**
   - Repository analysis requires linked GitHub account
   - Link account at: https://platform.aci.dev/appconfigs/GITHUB

4. **Network Issues**
   - Backend: http://localhost:5001
   - Frontend: http://localhost:5174
   - Check both servers are running

## 📊 Expected Response Examples

### **Config Analysis Response:**
```markdown
🔍 ## Resource Management
❌ Missing resource requests and limits for container 'nginx'

## Security  
⚠️ Container running as root user (runAsUser: 0)
⚠️ Privileged mode enabled

## Cost Optimization
💰 No LoadBalancer services found - good for cost optimization
```

### **Chat Response:**
```markdown
💬 Effective resource management in Kubernetes ensures optimal usage of cluster resources...

Key best practices include:
1. Always set resource requests and limits
2. Use horizontal pod autoscaling
3. Monitor resource utilization
```

### **Repository Analysis Response:**
```markdown
📊 **Repository Analysis: microsoft/vscode**

## Infrastructure as Code
✅ GitHub Actions workflows found
⚠️ Missing Kubernetes manifests

## Recommendations
1. Add deployment configurations
2. Implement resource monitoring
```

## 🎉 Success Indicators

✅ **Full Integration Working When:**
- All message types route correctly (check emoji indicators)
- File uploads trigger config analysis automatically  
- Repository names extracted from natural language
- Responses formatted properly with Markdown
- Error handling graceful for API limitations

## 🚀 Production Readiness

Your system is ready for production when:
- [ ] OpenAI API key configured (for GPT-4o classification)
- [ ] ACI.dev API key configured (for GitHub functions)
- [ ] GitHub account linked in ACI.dev platform
- [ ] All test scenarios passing
- [ ] Error handling tested
- [ ] File upload security verified

---

**🎯 Pro Tip:** Open browser developer tools to see detailed classification logs and network requests for debugging!
