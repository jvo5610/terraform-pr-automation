# Terraform-pr-automation

This is a github action created to run in automation Terraform or terragrunt in a pull request, you could then triggers plans by changes in terragrunt .tf or terragrunt.hcl files

## Action Inputs
---

| Variable     | Description    | Default | Required |
| ------------- | ------------- | -------- | -------- |
| LOG_LEVEL | Logging level | ERROR | False |
| TERRAFORM_VERSION | Terraform version | v1.5.3 | False |
| TERRAGRUNT_VERSION | Terragrunt version | v0.48.6 | False |
| TERRAGRUNT_DEPTH | Depth of the parent terragrunt.hcl file. E.g: aws/{path of terragrunt parent file} = 1 | 0 | False |
| IAC_TOOL | IAC Tool to be used TERRAGRUNT or TERRAFORM | TERRAGRUNT | True |
| EXCLUDED_DIRNAMES | Directory names to be skipped to run terraform or terragrunt | [".github", ".modules"] | False |

## Terraform usage example

---

```yaml
name: Terraform automation
on:
  pull_request:
  workflow_dispatch:
  issue_comment:
    types: [created]
permissions:
  actions: write
  contents: write
  id-token: write
  issues: write
  pull-requests: write

jobs:
  terraform_automation:
    runs-on: ubuntu-latest
    
    steps:
    - name: Check event_type
      id: check_event_type
      run: echo "is_issue_comment=${{ github.event_name == 'issue_comment' }}" >> $GITHUB_ENV

    - name: Checkout repository if event issue_coment
      if: env.is_issue_comment == 'true'
      uses: actions/checkout@v3
      with:
        ref: refs/pull/${{ github.event.issue.number }}/head

    - name: Checkout repository
      if: env.is_issue_comment == 'false'
      uses: actions/checkout@v3

    - name: Terraform automation
      uses: jvo5610/terraform-pr-automation@v0.1.0
      with:
        LOG_LEVEL: DEBUG
        IAC_TOOL: TERRAFORM
        EXCLUDED_DIRNAMES: '[".github", ".modules"]'
```

## Terragrunt usage example

---

```yaml
name: Terragrunt automation
on:
  pull_request:
  workflow_dispatch:
  issue_comment:
    types: [created]
permissions:
  actions: write
  contents: write
  id-token: write
  issues: write
  pull-requests: write

jobs:
  terragrunt_automation:
    runs-on: ubuntu-latest
    
    steps:
    - name: Check event_type
      id: check_event_type
      run: echo "is_issue_comment=${{ github.event_name == 'issue_comment' }}" >> $GITHUB_ENV

    - name: Checkout repository if event issue_coment
      if: env.is_issue_comment == 'true'
      uses: actions/checkout@v3
      with:
        ref: refs/pull/${{ github.event.issue.number }}/head

    - name: Checkout repository
      if: env.is_issue_comment == 'false'
      uses: actions/checkout@v3

    - name: Terragrunt automation
      uses: jvo5610/terraform-pr-automation@v0.1.0
      with:
        LOG_LEVEL: DEBUG
        IAC_TOOL: TERRAGRUNT
        EXCLUDED_DIRNAMES: '[".github", ".modules"]'
```

## PR Usage 
---

The action will check the changes on .tf and .hcl files in order to run a plan on each pul_request synchronize, this plan will be commented on the pull request. You will can run the commands `plan and apply` using terraform or terragrunt, note that this last one will give you also the posibility to run `terragrunt run-all` commands. `The path need to be appended at the end using -p flag, if not the root path will be the working directory for the command`

## PR Commands recommended
---

If not path -p provided the root path will be triggered

Comments / Commands:

```bash
terraform plan -p <working-dir>
terraform plan -destroy -p <working-dir>
terraform apply -p <working-dir>
terraform destroy -p <working-dir>

terragrunt plan -p <working-dir>
terragrunt plan -destroy -p <working-dir>
terragrunt apply -p <working-dir>
terragrunt destroy -p <working-dir>
terragrunt run-all plan -p <working-dir>
terragrunt run-all plan -destroy -p <working-dir>
terragrunt run-all apply -p <working-dir>
terragrunt run-all destroy -p <working-dir>
```
