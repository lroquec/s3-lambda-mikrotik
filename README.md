# S3-Lambda-Mikrotik

A serverless AWS Lambda function that processes Excel or CSV data files with network devices info and generates the Mikrotik script for monitoring said devices via netwatch.

## Overview

This project consists of a Lambda function that:
- Reads data from AWS S3 buckets
- Processes data using [pandas](https://pandas.pydata.org/)
- Generates Mikrotik router configuration scripts
- Normalizes column data
- Infrastructure as Code using [Terraform](https://www.terraform.io/)

## Prerequisites

- AWS Account
- [Python 3.x](https://www.python.org/)
- [Terraform](https://www.terraform.io/) >= 1.0
- Required Python packages:
  - pandas==2.0.3
  - numpy==1.24.3
  - openpyxl==3.1.2
  - [boto3](https://aws.amazon.com/sdk-for-python/)


## Project Structure

    s3-lambda-mikrotik/
    ├── README.md               # Project documentation
    ├── lambda_function.py      # Main Lambda function code
    ├── lambda_function.zip     # Packaged Lambda function
    ├── pandas-layer/          # Lambda layer for pandas dependencies
    │   ├── python/            # Python packages directory
    │   └── requirements.txt   # Python dependencies list
    ├── pandas_layer.zip       # Packaged Lambda layer
    ├── compute.tf             # Terraform compute resources configuration
    ├── provider.tf            # Terraform AWS provider configuration
    ├── s3.tf                  # Terraform S3 bucket configuration
    ├── shared_locals.tf       # Terraform shared local variables
    ├── variables.tf           # Terraform variables definition
    └── terraform.tfvars       # Terraform variables values

## Features

- S3 trigger integration
- Data processing with pandas
- Column name normalization
- Mikrotik script generation
- Infrastructure as Code with Terraform
- Lambda layer support for pandas

## Installation

1. Clone the repository:

    git clone https://github.com/yourusername/s3-lambda-mikrotik.git
    cd s3-lambda-mikrotik

2. Install dependencies in the pandas-layer directory:

    cd pandas-layer
    pip install -r requirements.txt -t python/
    cd ..

3. Install Terraform:

    # For macOS using Homebrew
    brew install terraform

    # For Windows using Chocolatey
    choco install terraform

    # For Linux (Debian/Ubuntu)
    wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg
    echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
    sudo apt update && sudo apt install terraform

    # For Linux (RHEL/CentOS)
    sudo yum install -y yum-utils
    sudo yum-config-manager --add-repo https://rpm.releases.hashicorp.com/RHEL/hashicorp.repo
    sudo yum -y install terraform

## Infrastructure Deployment

1. Initialize Terraform:

    terraform init

2. Review the infrastructure plan:

    terraform plan

3. Apply the infrastructure:

    terraform apply

## Configuration

1. Configure AWS credentials:

    aws configure

2. Update variables in terraform.tfvars

## Usage

The Lambda function automatically processes files uploaded to the configured S3 bucket **input_file_path** variable and generates a Mikrotik script based on the input data and saves it in S3 in the path defined by variable **output_file_path**.

## Infrastructure Cleanup

To destroy the AWS infrastructure:

    terraform destroy
