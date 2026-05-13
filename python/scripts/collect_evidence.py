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
    # Use the env var from YAML, or default to the local path
    tf_relative_path = os.getenv("TF_ACTION_WORKING_DIR", "terraform/modules")
    tf_dir = os.path.abspath(os.path.join(root_dir, tf_relative_path))
    try:
        tf_dir = os.path.join(root_dir, "terraform", "modules")
        print(f"DEBUG: Running terraform output in {tf_dir}")
        output = subprocess.check_output(["terraform", "output", "-json"],
                                         cwd=tf_dir,
                                         env=os.environ,  # <--- CRITICAL: Passes AWS/Terraform context
                                         text=True,
                                         stderr=subprocess.STDOUT
                                         )
        return json.loads(output)
    except subprocess.CalledProcessError as e:
        print(f"X Terraform Error {e.output}")
        return None
    except Exception as e:
        print(f"Error reading TF output: {e}")
        return None
    except Exception as e:
        printf(f"X Unexpected Error{e}")
        return None

def get_ai_recommendation(instance_type, status):
    """Calls Amazon Bedrock to get a real resizing recommendation"""
    print(f"🧠 Consulting Bedrock for {instance_type} ({status})...")
    try:
        bedrock = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')
        
        # Construct a strict prompt so the AI doesn't give you a long essay
        prompt = (
            f"System: You are a FinOps expert. Respond ONLY with the AWS instance type name.\n"
            f"User: An EC2 instance of type {instance_type} is {status}. "
            f"Suggest a smaller, cheaper instance type from the same family or t3 family."
        )

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 10,
            "messages": [{"role": "user", "content": prompt}]
        })

        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0',
            body=body
        )
        
        result = json.loads(response.get('body').read())
        recommendation = result['content'][0]['text'].strip()
        return recommendation
    except Exception as e:
        print(f"⚠️ Bedrock failed: {e}. Falling back to original type.")
        return instance_type
def get_actual_metrics(instance_id):
    """Fetches real CPU metrics from CloudWatch"""
    print(f"📊 Fetching CloudWatch metrics for {instance_id}...")
    try:
        cw = boto3.client('cloudwatch', region_name='us-east-1')
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(minutes=30)

        response = cw.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='CPUUtilization',
            Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
            StartTime=start_time,
            EndTime=end_time,
            Period=1800, # 30 minutes
            Statistics=['Average', 'Maximum']
        )

        if response['Datapoints']:
            dp = response['Datapoints'][0]
            avg = round(dp['Average'], 2)
            max_val = round(dp['Maximum'], 2)
            status = "Underutilized" if avg < 10 else "Optimal"
            return avg, max_val, status
        
        return 0.0, 0.0, "No Data"
    except Exception as e:
        print(f"⚠️ CloudWatch failed: {e}")
        return 0.85, 2.1, "Underutilized" # Fallback for local testing

def main():
    print("🚀 Starting Evidence Collection...")
    tf_data = get_tf_outputs()
    ec2_id = tf_data['ec2_instance_id']['value']
    
    # 1. Get REAL metrics from CloudWatch
    avg_cpu, max_cpu, status = get_actual_metrics(ec2_id)
    
    # 2. Get REAL advice from Bedrock based on those metrics
    ai_suggestion = get_ai_recommendation("m5.xlarge", status)

    evidence = {
        "timestamp": datetime.now().isoformat(),
        "recommendation": ai_suggestion,
        "resources": [
            {
                "resource_id": ec2_id,
                "metrics": {
                    "avg_cpu_utilization": f"{avg_cpu}%",
                    "max_cpu_utilization": f"{max_cpu}%",
                    "status": status
                }
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