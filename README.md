# AI Chat Interface with SageMaker

This project implements an AI chat interface using AWS SageMaker for model deployment and inference. The system uses a fine-tuned language model deployed on SageMaker endpoints to provide interactive chat capabilities.

## Project Structure

```
.
├── README.md
├── requirements.txt
└── src/
    ├── backend/
    │   ├── inference.py
    │   ├── 01-synthetic data generation.ipynb
    │   ├── 02-Finetune.ipynb
    │   ├── 03-Deploy.ipynb
    │   ├── 04-inference.ipynb
    │   ├── dataset.jsonl
    │   └── template.json
    └── infra/
        ├── samconfig.toml
        └── template.yaml
```

## Prerequisites

- Python 3.x
- AWS Account with appropriate permissions
- AWS CLI configured with appropriate credentials
- AWS SAM CLI installed (for infrastructure deployment)

## Dependencies

The project requires the following Python packages:
- boto3
- sagemaker

Install the dependencies using:
```bash
pip install -r requirements.txt
```

## Project Components

### 1. Data Generation and Model Training
- `01-synthetic data generation.ipynb`: Notebook for generating synthetic training data
- `02-Finetune.ipynb`: Notebook for fine-tuning the language model
- `dataset.jsonl`: Training dataset in JSONL format

### 2. Model Deployment
- `03-Deploy.ipynb`: Notebook for deploying the model to SageMaker
- `template.yaml`: AWS SAM template for infrastructure deployment
- `samconfig.toml`: SAM CLI configuration

### 3. Inference
- `inference.py`: Main inference script for interacting with the deployed model
- `04-inference.ipynb`: Notebook demonstrating model inference

## Usage

1. **Setup AWS Credentials**
   Ensure you have AWS credentials configured with appropriate permissions for SageMaker and other AWS services.

2. **Deploy Infrastructure**
   ```bash
   cd src/infra
   sam validate
   sam build
   sam deploy --no-confirm-changeset --no-fail-on-empty-changeset                
   ```

3. **Run the Chat Interface**
   ```bash
   cd src/backend
   python inference.py
   ```

## Features

- Interactive chat interface
- Streaming responses from the model
- Configurable model parameters (temperature, max tokens, etc.)
- Error handling and graceful exit options

## Configuration

The inference script can be configured by modifying the following parameters in `inference.py`:
- `PROFILE_NAME`: AWS profile name
- `REGION_NAME`: AWS region
- `ENDPOINT_NAME`: SageMaker endpoint name

## Model Parameters

The model inference can be customized by adjusting the following parameters:
- `max_new_tokens`: Maximum number of tokens to generate
- `temperature`: Controls randomness in the output
- `do_sample`: Whether to use sampling for generation
- `stop`: List of stop sequences

