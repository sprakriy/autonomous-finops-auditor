# Root main.tf
provider "aws" {
  region = "us-east-1"
}

module "financial_waste_lab" {
  source = "./terraform/modules"
  # You can add variables here later if needed
}

# Output the IDs so your Python script can find them easily
output "ec2_instance_id" {
  value = module.financial_waste_lab.audit_target_ec2_id
}