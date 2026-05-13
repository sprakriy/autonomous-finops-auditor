import boto3
import json
import subprocess
import os
from datetime import datetime

# Get the directory where THIS script is (python/scripts/)
script_dir = os.path.dirname(os.path.abspath(__file__))
current = script_dir
while current != os.path.dirname(current):
    if "terraform" in os.listdir(current):
        root_dir = current
        break
    current = os.path.dirname(current)
else:
    # Fallback to current working directory if the loop fails
    root_dir = os.getcwd()

print(f"✅ Root Directory identified as: {root_dir}")
decision_file = os.path.join(root_dir, "ai_decision.json")

def get_tf_outputs():
    """Extracts instance IDs directly from Terraform"""
    try:
        tf_dir = os.path.join(root_dir, "terraform", "modules")
        print(f"DEBUG: Running terraform output in {tf_dir}")
        output = subprocess.check_output(["terraform", "output", "-json"],
                                         cwd=root_dir,
                                         text=True,
                                         stderr=subprocess.STDOUT
                                         )
        return json.loads(output)
    except Exception as e:
        print(f"Error reading TF output: {e}")
        return None
    except Exception as e:
        printf(f"X Unexpected Error{e}")
        return None

def main():
    print("🚀 Starting Evidence Collection...")
    tf_data = get_tf_outputs()
    
    if not tf_data:
        print("❌ No Terraform outputs found. Is the infrastructure live?")
        return

    # Extract IDs from your root outputs
    ec2_id = tf_data['ec2_instance_id']['value']
    
    # Create the Evidence Object
    # We 'mock' the CPU to 0.8% to simulate waste without waiting 1 hour
    evidence = {
        "timestamp": datetime.now().isoformat(),
        "resources": [
            {
                "resource_id": ec2_id,
                "type": "m5.xlarge",
                "cost_per_hr": 0.192,
                "metrics": {
                    "avg_cpu_utilization": "0.85%",
                    "max_cpu_utilization": "2.1%",
                    "status": "Underutilized"
                },
                "hcl_context": "terraform/modules/main.tf"
            }
        ]
    }

    # Save to a local file so we can Destroy the AWS resources immediately
    with open(decision_file, "w") as f:
        json.dump(evidence, f, indent=4)
    
    print("✅ Evidence captured to ai_decision.json.")
    print("⚠️  You can now run 'terraform destroy' to stop the billing.")

if __name__ == "__main__":
    from datetime import datetime
    main()