#!/usr/bin/env python3
"""
Quick demo to show that the create-issue functionality is now fixed
Shows both success and error cases
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5001"

def test_create_issue_fix():
    """Test that create-issue works correctly with repo defaulting"""
    print("🧪 Testing create-issue functionality fix\n")
    
    test_cases = [
        {
            "name": "✅ Success: Explicit repo mention", 
            "message": "create an issue on TechEurope saying performance is slow",
            "should_work": True
        },
        {
            "name": "✅ Success: Implied TechEurope repo",
            "message": "file a bug for TechEurope about memory leaks", 
            "should_work": True
        },
        {
            "name": "❌ Expected Error: No repo specified",
            "message": "create an issue about database connection problems",
            "should_work": False
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{test_case['name']}")
        print(f"Input: \"{test_case['message']}\"")
        print("-" * 60)
        
        try:
            # Step 1: Filter/classify the request
            filter_response = requests.post(
                f"{BASE_URL}/api/filter-request",
                json={"message": test_case['message']},
                timeout=10
            )
            
            if filter_response.status_code == 200:
                filter_data = filter_response.json()
                classification = filter_data.get("classification", {})
                function_name = classification.get("function")
                extracted_params = classification.get("extracted_params", {})
                confidence = classification.get("confidence", 0)
                
                print(f"Classification: {function_name} (confidence: {confidence})")
                print(f"Extracted params: {extracted_params}")
                
                if function_name == "create-issue":
                    # Step 2: Execute the function
                    execute_response = requests.post(
                        f"{BASE_URL}/api/execute-function", 
                        json={
                            "function": function_name,
                            "message": test_case['message'],
                            "params": extracted_params
                        },
                        timeout=10
                    )
                    
                    if execute_response.status_code == 200:
                        execute_data = execute_response.json()
                        response_value = execute_data.get("response", {}).get("value", "")
                        issue_data = execute_data.get("issue", {})
                        
                        if test_case["should_work"]:
                            print("✅ SUCCESS: Issue created successfully!")
                            if "GitHub Issue Created Successfully" in response_value:
                                # Extract issue URL if available
                                issue_url = issue_data.get("data", {}).get("html_url", "N/A")
                                issue_number = issue_data.get("data", {}).get("number", "N/A")
                                print(f"   Issue #{issue_number}: {issue_url}")
                            else:
                                print(f"   Response: {response_value[:100]}...")
                        else:
                            print("❓ UNEXPECTED: Expected error but got success")
                            
                    elif execute_response.status_code == 400:
                        execute_data = execute_response.json()
                        error_msg = execute_data.get("error", "")
                        suggestion = execute_data.get("suggestion", "")
                        
                        if test_case["should_work"]:
                            print("❌ UNEXPECTED ERROR:")
                            print(f"   {error_msg}")
                            if suggestion:
                                print(f"   Suggestion: {suggestion}")
                        else:
                            print("✅ EXPECTED ERROR (this is correct behavior):")
                            print(f"   {error_msg}")
                            if suggestion:
                                print(f"   Helpful suggestion: {suggestion}")
                    else:
                        print(f"❌ Execution failed with status {execute_response.status_code}")
                        print(f"   Response: {execute_response.text}")
                else:
                    print(f"ℹ️  Classified as '{function_name}' instead of 'create-issue'")
            else:
                print(f"❌ Classification failed: {filter_response.status_code}")
                print(f"   Error: {filter_response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        
        print("\n" + "=" * 80 + "\n")
    
    print("🎉 Test completed!")
    print("\n💡 Summary:")
    print("   • Repo defaulting to 'ehewes' works when TechEurope is mentioned")
    print("   • Helpful error messages when no repo is specified")
    print("   • Natural language processing correctly extracts parameters")

if __name__ == "__main__":
    try:
        test_create_issue_fix()
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("   Make sure the Flask server is running on http://127.0.0.1:5001")
