[![Project generated with PyScaffold](https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold)](https://pyscaffold.org/)

# terraform-cloud-deployer

> Helper scripts for performing Terraform CI/CD operations

# Usage and Installation

For now, you clone this repo and run `pip install .`

It currently expects the environment variable `TERRAFORM_CLOUD_API_TOKEN` to be present, and set to a _team_ token that has access to the workspaces you will use it for. Then run `tfcd --help` for usage.

Runs are performed in two steps; building and uploading the configuration to Terraform Cloud, and starting a new run from that configuration. The TFC Configuration API is described [here](https://developer.hashicorp.com/terraform/cloud-docs/api-docs/configuration-versions), and the run API [here](https://developer.hashicorp.com/terraform/cloud-docs/api-docs/run).

The TL;DR is:

1. Package up both the Terraform files to be run, and any files they act on (for example, the Lambda code they might reference) into a zip file — currently, all Terraform files must be in the root directory — and upload them to TFC
1. Start a new run given the run configuration that the upload creates

This process is performed with the `tfcd configuration`, and `tfcd run` commands respectively:

```sh
$ tfcd -w data-development configuration create
# Will output a workspace ID
cv-thisisanexample
# Use the output above to start a run
$ tfcd -w data-development run start -c cv-thisisanexample
```

A new command which does both may be added in future, but it's a two step process for the moment in order to promote error handling for both steps. Of course you could disregard this recommmondation and easily combine them anyway, in the shell:

```sh
$ tfcd -w data-development configuration create | xargs tfcd -w data-development run start -c
```

## Docker

A convenience image for use with CI/CD tools such as Gitlab and Circle CI is available here:

`ghcr.io/guidionops/terraform-cloud-deployer:0.0.1`

with an `ENTRYPOINT` to the `tfcd` executable, so usage is simply:

```sh
docker run ghcr.io/guidionops/terraform-cloud-deployer:0.0.1 -w data-development run list
```

To put the above example in use as a job container then, you say something like:

```yaml
image: ghcr.io/guidionops/terraform-cloud-deployer:0.0.1
command: -w data-development run list
```
