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
