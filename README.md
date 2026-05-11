# autonomous-finops-auditor
# Autonomous FinOps Auditor 🚀

**An AI-driven governance agent that audits Terraform infrastructure for cost-efficiency.**

### 🎯 Objective
This project demonstrates a production-grade workflow for cloud cost optimization. It utilizes **Claude 4.6 Sonnet** to evaluate live AWS utilization data against **Terraform** manifests, providing automated remediation reports.

### 🛠️ Tech Stack
* **Cloud Infrastructure:** AWS (EC2, RDS)
* **IaC:** Terraform
* **AI Engine:** Anthropic Claude 4.6 (via Amazon Bedrock)
* **Security:** GitHub OIDC Identity Federation (Zero-Trust)
* **Logic:** Python 3.x (Boto3)

### ⚙️ Workflow
1. **Provision:** Deploy "intentionally over-provisioned" resources via Terraform.
2. **Audit:** Python script collects CloudWatch metrics and S3-backend state.
3. **Analyze:** Claude 4.6 evaluates the delta between "Planned Cost" vs "Actual Usage."
4. **Report:** Automated GitHub Action generates a FinOps remediation summary.
