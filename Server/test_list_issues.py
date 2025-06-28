#!/usr/bin/env python3
"""
Test script for the new GITHUB__LIST_ISSUES functionality
Demonstrates the full end-to-end flow for listing GitHub issues.
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5001"

def test_list_issues_flow():
    """Test the complete list issues flow"""
    print("🧪 Testing GITHUB__LIST_ISSUES functionality\n")
    
    # Test cases for different ways to request listing issues
    test_cases = [
        "list issues from TechEurope",
        "show me issues in TechEurope", 
        "what issues are open in TechEurope",
        "get issues for ehewes/TechEurope",
        "view issues from the TechEurope repo"
    ]
    
    for i, message in enumerate(test_cases, 1):
        print(f"📋 Test Case {i}: '{message}'")
        print("-" * 50)
        
        # Step 1: Filter the request
        filter_response = requests.post(
            f"{BASE_URL}/api/filter-request",
            json={"message": message}
        )
        
        if filter_response.status_code == 200:
            filter_data = filter_response.json()
            classification = filter_data.get("classification", {})
            function_name = classification.get("function")
            extracted_params = classification.get("extracted_params", {})
            confidence = classification.get("confidence", 0)
            
            print(f"✅ Classification: {function_name} (confidence: {confidence})")
            print(f"   Extracted params: {extracted_params}")
            
            # Step 2: Execute the function if it's list-issues
            if function_name == "list-issues":
                execute_response = requests.post(
                    f"{BASE_URL}/api/execute-function",
                    json={
                        "function": function_name,
                        "message": message,
                        "params": extracted_params
                    }
                )
                
                if execute_response.status_code == 200:
                    execute_data = execute_response.json()
                    count = execute_data.get("count", 0)
                    repository = execute_data.get("repository", "")
                    response_value = execute_data.get("response", {}).get("value", "")
                    
                    print(f"✅ Execution successful:")
                    print(f"   Repository: {repository}")
                    print(f"   Issues found: {count}")
                    print(f"   Response: {response_value[:100]}...")
                    
                    # Show first issue if available
                    issues_data = execute_data.get("issues", {}).get("data", [])
                    if issues_data:
                        first_issue = issues_data[0]
                        print(f"   First issue: #{first_issue.get('number')} - {first_issue.get('title')}")
                        print(f"   Issue URL: {first_issue.get('html_url')}")
                else:
                    print(f"❌ Execution failed: {execute_response.status_code}")
                    print(f"   Error: {execute_response.text}")
            else:
                print(f"ℹ️  Classified as '{function_name}' instead of 'list-issues'")
        else:
            print(f"❌ Filtering failed: {filter_response.status_code}")
            print(f"   Error: {filter_response.text}")
        
        print("\n")

def test_direct_list_issues_endpoint():
    """Test the direct /api/list-issues endpoint"""
    print("🎯 Testing direct /api/list-issues endpoint\n")
    
    response = requests.post(
        f"{BASE_URL}/api/list-issues",
        json={
            "repo_owner": "ehewes",
            "repo_name": "TechEurope"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Direct endpoint test successful:")
        print(f"   Status: {data.get('status')}")
        print(f"   Repository: {data.get('repository')}")
        
        issues = data.get("issues", {}).get("data", [])
        print(f"   Total issues: {len(issues)}")
        
        for issue in issues:
            print(f"   - Issue #{issue.get('number')}: {issue.get('title')}")
            print(f"     State: {issue.get('state')} | URL: {issue.get('html_url')}")
    else:
        print(f"❌ Direct endpoint test failed: {response.status_code}")
        print(f"   Error: {response.text}")

if __name__ == "__main__":
    try:
        print("=" * 60)
        print("🚀 GITHUB__LIST_ISSUES Integration Test")
        print("=" * 60)
        print()
        
        test_list_issues_flow()
        test_direct_list_issues_endpoint()
        
        print("=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to Flask server.")
        print("   Make sure the server is running on http://127.0.0.1:5001")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
