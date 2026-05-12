import re
import json
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(script_dir, "../../"))
decision_file = os.path.join(root_dir, "ai_decision.json")

def run_remediation():
    # 1. Load the recommendation from the previous step
    # We assume your AI script saved its decision to this JSON file
    try:
        with open(decision_file, 'r') as f:
            decision = json.load(f)
        new_type = decision.get('recommendation')
    except FileNotFoundError:
        print("Error: No AI decision file found. Run the audit first.")
        return

    # 2. Configuration
    target_file = "terraform/modules/main.tf"
    resource_id = "audit_target_ec2"

    if not os.path.exists(target_file):
        print(f"Error: Could not find {target_file}")
        return

    with open(target_file, 'r') as f:
        content = f.read()

    # 3. The "Surgical" Regex
    # This pattern finds the resource block and captures the 'instance_type =' part
    # up until the quoted value, ensuring it only targets 'audit_target_ec2'.
    pattern = rf'(resource\s+"aws_instance"\s+"{resource_id}"\s+{{.*?instance_type\s+=\s+)"[^"]+"'
    replacement = rf'\1"{new_type}"'

    # Using DOTALL so the '.*?' matches across multiple lines/newlines
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    # 4. Write the change back to the file
    with open(target_file, 'w') as f:
        f.write(new_content)

    print(f"✅ Day 5 Success: {resource_id} updated to {new_type} in {target_file}")

if __name__ == "__main__":
    run_remediation()