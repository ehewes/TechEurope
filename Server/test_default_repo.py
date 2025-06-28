#!/usr/bin/env python3
"""
Test script to verify that create-issue defaults to TechEurope repository
when no repository is specified in the user message.
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_create_issue_with_default_repo():
    """Test creating an issue without specifying a repository"""
    
    filter_url = "http://localhost:5001/api/filter-request"
    execute_url = "http://localhost:5001/api/execute-function"
    
    # Test message that doesn't specify any repository
    test_message = "create an issue about fixing the authentication bug in the login system"
    
    print("Testing create-issue with default repository...")
    print(f"Message: {test_message}")
    print("-" * 50)
    
    try:
        # Step 1: Filter/classify the request
        filter_payload = {
            "message": test_message,
            "has_file": False
        }
        
        filter_response = requests.post(filter_url, json=filter_payload, headers={"Content-Type": "application/json"}, timeout=30)
        
        if filter_response.status_code != 200:
            print(f"❌ Filter request failed with status {filter_response.status_code}")
            print(filter_response.text)
            return
        
        filter_result = filter_response.json()
        classification = filter_result.get('classification', {})
        function_name = classification.get('function')
        extracted_params = classification.get('extracted_params', {})
        
        print(f"Classified as: {function_name}")
        print(f"Extracted params: {extracted_params}")
        
        # Step 2: Execute the function
        execute_payload = {
            "function": function_name,
            "message": test_message,
            "params": extracted_params
        }
        
        execute_response = requests.post(execute_url, json=execute_payload, headers={"Content-Type": "application/json"}, timeout=30)
        
        print(f"Status Code: {execute_response.status_code}")
        print("Response:")
        
        if execute_response.headers.get('content-type', '').startswith('application/json'):
            response_data = execute_response.json()
            print(json.dumps(response_data, indent=2))
            
            # Check if it successfully defaulted to TechEurope
            if execute_response.status_code == 200:
                response_value = response_data.get('response', {}).get('value', '')
                if 'ehewes/TechEurope' in response_value or 'TechEurope' in response_value:
                    print("\n✅ SUCCESS: Issue was created in the default TechEurope repository!")
                else:
                    print("\n⚠️  WARNING: Issue created but may not be in TechEurope repo")
                    print(f"Response contains: {response_value[:200]}...")
            else:
                print(f"\n❌ ERROR: Request failed with status {execute_response.status_code}")
        else:
            print(execute_response.text)
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        print("Raw response:", execute_response.text)

def test_list_issues_with_default_repo():
    """Test listing issues without specifying a repository"""
    
    url = "http://localhost:5001/api/execute-function"
    
    # Test message that doesn't specify any repository
    test_message = "show me the current issues"
    
    payload = {
        "message": test_message
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print("\n" + "="*60)
    print("Testing list-issues with default repository...")
    print(f"Message: {test_message}")
    print("-" * 50)
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print("Response:")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            response_data = response.json()
            print(json.dumps(response_data, indent=2))
            
            # Check if it successfully defaulted to TechEurope
            if response.status_code == 200:
                result = response_data.get('result', {})
                if 'TechEurope' in str(result):
                    print("\n✅ SUCCESS: Issues listed from the default TechEurope repository!")
                else:
                    print("\n⚠️  WARNING: Issues listed but may not be from TechEurope repo")
            else:
                print(f"\n❌ ERROR: Request failed with status {response.status_code}")
        else:
            print(response.text)
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        print("Raw response:", response.text)

if __name__ == "__main__":
    print("🧪 Testing Default Repository Functionality")
    print("=" * 60)
    
    # Test both create-issue and list-issues with default repo
    test_create_issue_with_default_repo()
    test_list_issues_with_default_repo()
    
    print("\n" + "="*60)
    print("✅ Default repository tests completed!")
