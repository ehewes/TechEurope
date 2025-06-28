#!/usr/bin/env python3
"""
Test script to verify that create-issue defaults to TechEurope repository
when no repository is specified in the user message.
"""

import requests
import json

def test_default_repo_functionality():
    """Test that messages without explicit repos default to TechEurope"""
    
    filter_url = "http://localhost:5001/api/filter-request"
    execute_url = "http://localhost:5001/api/execute-function"
    
    test_cases = [
        {
            "name": "Create Issue Without Repo",
            "message": "create an issue saying we need to fix the database connection",
            "expected_function": "create-issue"
        },
        {
            "name": "List Issues Without Repo", 
            "message": "show me the current issues",
            "expected_function": "list-issues"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{'='*60}")
        print(f"🧪 Testing: {test_case['name']}")
        print(f"Message: {test_case['message']}")
        print("-" * 50)
        
        try:
            # Step 1: Classify the request
            filter_payload = {
                "message": test_case['message'],
                "has_file": False
            }
            
            filter_response = requests.post(filter_url, json=filter_payload, timeout=30)
            
            if filter_response.status_code != 200:
                print(f"❌ Classification failed: {filter_response.status_code}")
                continue
            
            filter_result = filter_response.json()
            classification = filter_result.get('classification', {})
            function_name = classification.get('function')
            extracted_params = classification.get('extracted_params', {})
            
            print(f"✅ Classified as: {function_name}")
            print(f"📋 Extracted params: {extracted_params}")
            
            if function_name != test_case['expected_function']:
                print(f"⚠️  Expected {test_case['expected_function']}, got {function_name}")
                continue
            
            # Step 2: Execute the function
            execute_payload = {
                "function": function_name,
                "message": test_case['message'],
                "params": extracted_params
            }
            
            execute_response = requests.post(execute_url, json=execute_payload, timeout=30)
            
            print(f"📡 Execute Status: {execute_response.status_code}")
            
            if execute_response.status_code == 200:
                response_data = execute_response.json()
                response_value = response_data.get('response', {}).get('value', '')
                
                # Check if TechEurope is mentioned in the response
                if 'TechEurope' in response_value and 'ehewes' in response_value:
                    print("✅ SUCCESS: Defaulted to ehewes/TechEurope repository!")
                    print(f"🎯 Response preview: {response_value[:150]}...")
                else:
                    print("❌ FAILED: Response doesn't mention TechEurope")
                    print(f"📄 Full response: {json.dumps(response_data, indent=2)}")
            else:
                response_data = execute_response.json() if execute_response.headers.get('content-type', '').startswith('application/json') else {}
                error_msg = response_data.get('error', 'Unknown error')
                print(f"❌ Execution failed: {error_msg}")
                
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")

if __name__ == "__main__":
    print("🚀 Testing Default Repository Functionality")
    print("This test verifies that when no repository is specified,")
    print("the system defaults to ehewes/TechEurope")
    
    test_default_repo_functionality()
    
    print("\n" + "="*60)
    print("✅ Test completed!")
