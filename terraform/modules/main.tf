# Use the tags to help your Python script filter the "waste"
locals {
  common_tags = {
    Project     = "FinOps-Audit-Lab"
    Environment = "Sandbox"
    Owner       = "Senior-Architect"
  }
}

# Over-provisioned EC2: Using an m5.xlarge instead of a t3.micro
data "aws_ssm_parameter" "al2023_ami" {
  name = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"
}

# 2. Use the dynamic ID in your EC2 resource
resource "aws_instance" "audit_target_ec2" {
  # This pulls the value from the SSM parameter lookup above
  ami           = data.aws_ssm_parameter.al2023_ami.value
  instance_type = "m5.xlarge" # Expensive for testing
  
  tags = merge(local.common_tags, {
    Name = "Heavy-Compute-Instance"
  })
}

# Over-provisioned RDS: db.m5.large with high Provisioned IOPS
resource "aws_db_instance" "audit_target_rds" {
  allocated_storage      = 100
  db_name                = "bloated_db"
  engine                 = "mysql"
  engine_version         = "8.0"
  instance_class         = "db.m5.large" # Expensive for testing
  username               = "admin"
  password               = "ForbiddenPassword123!" # In real life, use your S3/OIDC logic
  parameter_group_name   = "default.mysql8.0"
  skip_final_snapshot    = true
  
  # Provisioned IOPS (io1) is a major cost driver
  storage_type           = "io1"
  iops                   = 1000 

  tags = local.common_tags
}