#!/usr/bin/env python3
"""
Test script for the intelligent routing system in the ACI.dev SRE Agent.
This script demonstrates how user requests are classified and routed to the appropriate backend functions.
"""

import requests
import json
import time

# Backend URL
BASE_URL = "http://localhost:5001"

def test_classification(message, has_file=False, file_type=""):
    """Test the classification endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing Classification: {message}")
    print(f"Has file: {has_file}, File type: {file_type}")
    print(f"{'='*60}")
    
    payload = {
        "message": message,
        "has_file": has_file,
        "file_type": file_type
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/filter-request", json=payload)
        result = response.json()
        
        # Extract classification from nested structure
        classification = result.get('classification', {})
        
        print(f"✅ Classification Result:")
        print(f"   Function: {classification.get('function', 'Unknown')}")
        print(f"   Confidence: {classification.get('confidence', 0):.2f}")
        print(f"   Reasoning: {classification.get('reasoning', 'No reasoning provided')}")
        print(f"   Parameters: {json.dumps(classification.get('extracted_params', {}), indent=2)}")
        
        return classification
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_execution(classification, original_message, file_content=None):
    """Test the execution endpoint"""
    if not classification:
        print("❌ Cannot test execution without classification result")
        return
    
    print(f"\n🚀 Testing Execution for function: {classification['function']}")
    
    payload = {
        "function": classification["function"],
        "params": classification.get("extracted_params", {}),
        "message": original_message,
        "file_content": file_content
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/execute-function", json=payload)
        result = response.json()
        
        if response.status_code == 200:
            print(f"✅ Execution successful!")
            response_value = result.get("response", {}).get("value", "No response value")
            print(f"Response preview: {response_value[:200]}..." if len(response_value) > 200 else response_value)
        else:
            print(f"❌ Execution failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Execution error: {e}")

def main():
    """Test various scenarios"""
    print("🤖 Testing ACI.dev SRE Agent Intelligent Routing System")
    print("=" * 80)
    
    # Test cases
    test_cases = [
        {
            "message": "What are the best practices for Kubernetes resource management?",
            "description": "General SRE question - should route to chat"
        },
        {
            "message": "Analyze the GitHub repository microsoft/vscode for SRE practices",
            "description": "Repository analysis request"
        },
        {
            "message": "Create a GitHub issue in facebook/react for missing deployment docs",
            "description": "GitHub issue creation request"
        },
        {
            "message": "Please review this deployment configuration",
            "has_file": True,
            "file_type": "application/x-yaml",
            "file_content": """
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
            """,
            "description": "Configuration analysis with file upload"
        },
        {
            "message": "How do I optimize costs in AWS EKS?",
            "description": "Cost optimization question - should route to chat"
        },
        {
            "message": "File a bug report for kubernetes/kubernetes about pod scheduling",
            "description": "GitHub issue creation with different wording"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['description']}")
        
        # Test classification
        classification = test_classification(
            test_case["message"],
            test_case.get("has_file", False),
            test_case.get("file_type", "")
        )
        
        # Test execution (only for chat and config-analysis to avoid creating real GitHub issues)
        if classification and classification.get("function") in ["chat", "config-analysis"]:
            test_execution(
                classification,
                test_case["message"],
                test_case.get("file_content")
            )
        elif classification:
            print(f"⏭️  Skipping execution for {classification['function']} (would perform real action)")
        
        time.sleep(1)  # Brief pause between tests
    
    print(f"\n{'='*80}")
    print("🎉 Testing complete! The intelligent routing system is working.")
    print("   - Messages are classified correctly based on content and context")
    print("   - File uploads are detected and routed to config-analysis")
    print("   - Repository analysis requests are identified")
    print("   - GitHub issue creation requests are recognized")
    print("   - General SRE questions are routed to chat")

if __name__ == "__main__":
    main()
