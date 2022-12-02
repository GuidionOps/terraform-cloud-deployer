[![Project generated with PyScaffold](https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold)](https://pyscaffold.org/)

# terraform-cloud-deployer

> Helper scripts for performing Terraform CI/CD operations

# Usage and Installation

For now, you clone this repo and run `pip install .`

It currently expects the environment variable `TERRAFORM_CLOUD_API_TOKEN` to be present, and set to a _team_ token that has access to the workspaces you will use it for.

Then run `tfcd --help` for usage.
