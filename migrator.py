#!/usr/bin/env python3
"""
Apigee Migrator - Export from Apigee and adapt for non-GCP platforms.
Focus: Proxies, Policies, Shared Flows → Portable configs (Kong YAML, etc.)
"""

import argparse
import json
import os
import requests
import zipfile
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List

class ApigeeMigrator:
    def __init__(self, base_url: str, org: str, username: Optional[str] = None, 
                 password: Optional[str] = None, token: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.org = org
        self.auth = (username, password) if username and password else None
        self.headers = {"Authorization": f"Bearer {token}"} if token else {}
        self.session = requests.Session()
        if self.headers:
            self.session.headers.update(self.headers)

    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}/organizations/{self.org}{endpoint}"
        if self.auth:
            return self.session.request(method, url, auth=self.auth, **kwargs)
        return self.session.request(method, url, **kwargs)

    def list_proxies(self) -> List[str]:
        """List all API proxies in the organization."""
        resp = self._request("GET", "/apis")
        resp.raise_for_status()
        return resp.json()

    def get_latest_revision(self, proxy_name: str) -> str:
        """Get the latest revision number for a proxy."""
        resp = self._request("GET", f"/apis/{proxy_name}/revisions")
        resp.raise_for_status()
        revisions = resp.json()
        if not revisions:
            raise ValueError(f"No revisions found for proxy {proxy_name}")
        return max(revisions, key=int)

    def export_proxy(self, proxy_name: str, revision: Optional[str] = None) -> Path:
        """Export a specific proxy as a ZIP bundle."""
        if not revision or revision == "latest":
            revision = self.get_latest_revision(proxy_name)
        
        resp = self._request("GET", f"/apis/{proxy_name}/revisions/{revision}?format=bundle")
        resp.raise_for_status()
        
        out_dir = Path("exports/proxies")
        out_dir.mkdir(parents=True, exist_ok=True)
        
        out_path = out_dir / f"{proxy_name}_rev{revision}.zip"
        out_path.write_bytes(resp.content)
        print(f"✅ Exported {proxy_name} (rev {revision}) to {out_path}")
        return out_path

    def export_all_proxies(self):
        """Export all proxies in the organization."""
        proxies = self.list_proxies()
        print(f"Found {len(proxies)} proxies. Starting export...")
        
        for proxy in proxies:
            try:
                self.export_proxy(proxy)
            except Exception as e:
                print(f"❌ Failed to export {proxy}: {e}")

    def proxy_to_kong(self, zip_path: Path) -> Dict:
        """Basic transformation: Apigee proxy ZIP → Kong declarative YAML."""
        extract_dir = zip_path.with_suffix('')
        extract_dir.mkdir(exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(extract_dir)
        
        # Parse basic proxy info (simplified - extend for full XML parsing)
        proxy_name = zip_path.stem.split('_rev')[0]
        
        kong_config: Dict[str, Any] = {
            "_format_version": "3.0",
            "services": [
                {
                    "name": proxy_name,
                    "url": "http://your-upstream-backend.example.com",  # TODO: customize
                    "routes": [
                        {
                            "name": f"{proxy_name}-route",
                            "paths": ["/api/v1"],  # TODO: extract from Apigee proxy
                            "methods": ["GET", "POST", "PUT", "DELETE"]
                        }
                    ]
                }
            ],
            "plugins": [
                # Example mappings - extend based on Apigee policies
                {"name": "rate-limiting", "config": {"minute": 1000}},
                {"name": "cors"}
            ]
        }
        
        # Save Kong declarative config
        yaml_path = zip_path.with_suffix('.kong.yml')
        with open(yaml_path, 'w') as f:
            yaml.dump(kong_config, f, default_flow_style=False, sort_keys=False)
        
        print(f"✅ Generated Kong config: {yaml_path}")
        return kong_config

    def export_all(self):
        """Full basic export."""
        Path("exports").mkdir(exist_ok=True)
        self.export_all_proxies()
        print("\nExport complete. Run '--action to-kong' to generate target configs.")

def main():
    parser = argparse.ArgumentParser(
        description="Apigee Migrator - Export and transform Apigee configs for open platforms",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument("--base-url", default="https://api.enterprise.apigee.com",
                        help="Apigee Management API base URL")
    parser.add_argument("--org", required=True, help="Apigee Organization name")
    parser.add_argument("--user", help="Apigee username (email)")
    parser.add_argument("--pass", dest="password", help="Apigee password")
    parser.add_argument("--token", help="Bearer token (alternative to user/pass)")
    parser.add_argument("--action", choices=["list", "export", "to-kong", "export-all"], 
                        required=True, help="Action to perform")
    parser.add_argument("--proxy", help="Specific proxy name (for export)")
    
    args = parser.parse_args()
    
    if not args.token and not (args.user and args.password):
        parser.error("Either --token or both --user and --pass are required")
    
    migrator = ApigeeMigrator(
        base_url=args.base_url,
        org=args.org,
        username=args.user,
        password=args.password,
        token=args.token
    )
    
    if args.action == "list":
        proxies = migrator.list_proxies()
        print("Available proxies:")
        for p in proxies:
            print(f"  - {p}")
    
    elif args.action in ["export", "export-all"]:
        if args.proxy and args.action == "export":
            migrator.export_proxy(args.proxy)
        else:
            migrator.export_all()
    
    elif args.action == "to-kong":
        exports_dir = Path("exports/proxies")
        if not exports_dir.exists():
            print("No exports found. Run export first.")
            return
        
        for zip_file in exports_dir.glob("*.zip"):
            try:
                migrator.proxy_to_kong(zip_file)
            except Exception as e:
                print(f"Failed to convert {zip_file}: {e}")

if __name__ == "__main__":
    main()
