# Apigee Migrator

A Python CLI tool to export Apigee configurations from Google Cloud and transform them into portable formats for other API gateways (Kong, Tyk, Gravitee, Envoy, etc.).

This tool helps break free from GCP lock-in by exporting proxies, policies, and other artifacts in neutral formats.

## Features

- Export Apigee API Proxies as ZIP bundles
- Basic transformation to Kong declarative YAML
- List all proxies in an organization
- Extensible for more targets and policy mappings

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/apigee-migrator.git
cd apigee-migrator
pip install -e .

Usage
Authentication
You can use either username/password or a Bearer token.
Bash# List all proxies
apigee-migrator --org YOUR_ORG --user YOUR_EMAIL --pass YOUR_PASS --action list

# Export all proxies
apigee-migrator --org YOUR_ORG --user YOUR_EMAIL --pass YOUR_PASS --action export

# Export specific proxy
apigee-migrator --org YOUR_ORG --user YOUR_EMAIL --pass YOUR_PASS --action export --proxy my-proxy-name

# Transform exported proxies to Kong config
apigee-migrator --org YOUR_ORG --user YOUR_EMAIL --pass YOUR_PASS --action to-kong
Using token:
Bashapigee-migrator --org YOUR_ORG --token YOUR_BEARER_TOKEN --action export
