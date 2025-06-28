import requests
import argparse
import json

API_URL = "http://127.0.0.1:5001/check-config"

def analyze_configuration(file_path):
    print(f"Analysing YAML file: {file_path}")

    try:
        with open(file_path, 'r') as f:
            yaml_content = f.read()

        data = {"config": yaml_content}

        print("Sending Configuration to SRE Agent...")
        response = requests.post(API_URL, json=data)
        response.raise_for_status()

        breakdown = response.json()

        print("\n" + "="*50)
        print("SRE Agent Report")
        print("="*50 + "\n")
        
        if breakdown.get('status') == 'success':
            print(breakdown.get('Breakdown', 'No breakdwon found.'))
        else:
            print(f"Breakdown failed: {breakdown.get('error', 'Unknown error')}")

        print("\n" + "="*50)


    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except requests.exceptions.RequestException as e:
        print(f"Error: Could not connect to the SRE Agent API at {API_URL}.")
        print(f"Please ensure the Flask server (app.py) is running.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="SRE Agent: Analysis of Deployment Configurations."
    )
    parser.add_argument(
        "filepath",
        type=str,
        help="Path to the YAML configuration file to breakdown."
    )
    args = parser.parse_args()

    analyze_configuration(args.filepath)