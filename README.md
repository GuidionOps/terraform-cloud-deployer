[![Project generated with PyScaffold](https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold)](https://pyscaffold.org/)

> Helper scripts for performing Terraform CI/CD operations

Note that this repository doubles up both for the Python package, and the Circle CI Orb that uses it. There are separate instructions detailed for usage and deployments of each.

If you are using Circle CI, the easiest way to get started is to use the [Orb](#usage-example), else you can use the Docker image, or even the package itself directly to create your own flows.

- [Usage and Installation](#usage-and-installation)
  - [Docker](#docker)
  - [Deploying](#deploying)
- [Circle CI 'Orb'](#circle-ci-orb)
  - [Usage Example](#usage-example)
  - [Deploying](#deploying-1)

# Usage and Installation

For now, you clone this repo and run `pip install .`

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
tfcd -w data-development configuration create | xargs tfcd -w data-development run start -c
```

## Docker

A convenience image for use with CI/CD tools such as Gitlab and Circle CI is available here:

`ghcr.io/guidionops/terraform-cloud-deployer:0.0.2`

with an `ENTRYPOINT` to the `tfcd` executable, so usage is simply:

```sh
docker run ghcr.io/guidionops/terraform-cloud-deployer:0.0.2 -w data-development run list
```

To put the above example in use as a job container then, you say something like:

```yaml
image: ghcr.io/guidionops/terraform-cloud-deployer:0.0.2
command: -w data-development run list
```

## Deploying

Simply push a new tag, and Github Actions will create a new Docker tag here:

```sh
ghcr.io/guidionops/terraform-cloud-deployer:[TAG]
```

# Circle CI 'Orb'

This repo is doubling up as the source for a Circle CI Orb called `guidionops/iac-deployer`.

The orb uses this repo's [terraform-cloud-deployer](https://github.com/GuidionOps/terraform-cloud-deployer) package ([Docker image](https://github.com/GuidionOps/terraform-cloud-deployer/pkgs/container/terraform-cloud-deployer)) to piece together the tasks necessary for a complete workflow which executes runs on Terraform Cloud. See that repo for details of how this works.

## Usage Example

```yaml
version: 2.1

orbs:
  iac-deployer: guidionops/iac-deployer@dev:first

workflows:
  deploy_to_development:
    jobs:
      - iac-deployer/deploy:
          workspace: web-development
          code_directory: './lambdas'
          slack_channel: 'afrazs-random-channel-of-madness'
          slack_access_token: $SLACK_ACCESS_TOKEN
          context:
            - org-global
            - global
            - web-development
          filters:
            branches:
              only:
                - development
```

The Terraform directory — which can be set with the flag `-t` to our `tfcd` program — is hardcoded to `.`, so make sure all of your Terraform code is in the root folder.

## Deploying

Although the orb file is named `terraform-cloud-deployer.yaml`, it's actually deployed to the name `iac-deployer`. This is to maintain API abstraction for developer usage, and means we are unshackled from specific tooling.

It's also important to understand that the orb versions have no relation to git tags, hashes, or anything else. They're automatically incremented with the relevant `circleci` publish command (see below). This means that although — strictly speaking — this isn't the proper place for the orb file, it has no practical effect, since completely different publication methods are in use. If we were to use something like Gitlab in future though, then this file should move home to it's own repo.

Test changes with:

```sh
circleci orb publish terraform-cloud-deployer.yaml guidionops/iac-deployer@dev:first
```

which will give you `guidionops/iac-deployer@dev:first` to use in your Circle CI configurations.

Once you have a new version ready, push with:

```sh
circleci orb publish promote guidionops/iac-deployer@dev:first patch
```

and you can use `guidionops/iac-deployer@dev:[TAG YOU GOT BACK]` in configurations.
