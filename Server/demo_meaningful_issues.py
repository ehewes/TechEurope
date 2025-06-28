#!/usr/bin/env python3
"""
Demo showcasing the improved GITHUB__LIST_ISSUES functionality
Before: Generic message
After: Meaningful, formatted issue data
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5001"

def demo_meaningful_list_issues():
    """Demonstrate the improved list issues functionality"""
    print("=" * 80)
    print("🎯 DEMO: Meaningful GitHub Issues Data")
    print("=" * 80)
    print()
    
    # Test the improved list issues functionality
    test_cases = [
        {
            "description": "Natural language request",
            "message": "show me issues in TechEurope"
        },
        {
            "description": "Direct question format", 
            "message": "what issues are open in TechEurope?"
        },
        {
            "description": "List command format",
            "message": "list issues from TechEurope"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"📋 Test {i}: {test_case['description']}")
        print(f"   Input: \"{test_case['message']}\"")
        print("-" * 50)
        
        try:
            # Step 1: Filter the request
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
                
                print(f"✅ Classification: {function_name} (confidence: {confidence})")
                print(f"   Extracted: {extracted_params}")
                
                if function_name == "list-issues":
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
                        count = execute_data.get("count", 0)
                        repository = execute_data.get("repository", "")
                        response_value = execute_data.get("response", {}).get("value", "")
                        
                        print(f"✅ Found {count} issues in {repository}")
                        print("\n📋 FORMATTED RESPONSE:")
                        print("-" * 40)
                        print(response_value)
                        print("-" * 40)
                        
                        # Show raw data summary
                        issues_data = execute_data.get("issues", {}).get("data", [])
                        if issues_data:
                            print(f"\n📊 RAW DATA SUMMARY:")
                            for issue in issues_data[:2]:  # Show first 2 issues
                                print(f"   • Issue #{issue.get('number')}: {issue.get('title')}")
                                print(f"     State: {issue.get('state')} | Author: {issue.get('user', {}).get('login', 'N/A')}")
                                print(f"     URL: {issue.get('html_url', 'N/A')}")
                    else:
                        print(f"❌ Execution failed: {execute_response.status_code}")
                        print(f"   Error: {execute_response.text}")
                else:
                    print(f"ℹ️  Classified as '{function_name}' instead of 'list-issues'")
            else:
                print(f"❌ Classification failed: {filter_response.status_code}")
                print(f"   Error: {filter_response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        
        print("\n" + "=" * 80 + "\n")
    
    print("🎉 Demo completed!")
    print("\n💡 Key improvements:")
    print("   • Natural language understanding")
    print("   • Rich, formatted markdown output")
    print("   • Issue details: title, author, date, labels, links")
    print("   • Summary statistics and repository links")
    print("   • Human-readable issue descriptions")
    print("   • Professional formatting for SRE teams")

if __name__ == "__main__":
    try:
        demo_meaningful_list_issues()
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("   Make sure the Flask server is running on http://127.0.0.1:5001")
