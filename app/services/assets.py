"""
Asset optimization service for ChosyTable
Handles CSS/JS bundling, minification, and compression
"""

import os
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from flask import current_app, url_for
import logging

logger = logging.getLogger(__name__)

class AssetOptimizer:
    """Optimizes and bundles static assets for better performance"""
    
    def __init__(self, static_folder: str = None):
        self.static_folder = static_folder or current_app.static_folder
        self.manifest_file = os.path.join(self.static_folder, 'manifest.json')
        self.bundles = {
            'css': {
                'core': [
                    'bootstrap/css/bootstrap.min.css',
                    'css/fontawesome.css',
                    'css/templatemo-space-dynamic.css',
                    'css/animated.css',
                    'css/owl.css',
                    'styles/main.css'
                ]
            },
            'js': {
                'core': [
                    'jquery/jquery.min.js',
                    'bootstrap/js/bootstrap.bundle.min.js',
                    'js/animation.js',
                    'js/imagesloaded.js',
                    'js/isotope.js',
                    'js/owl-carousel.js',
                    'js/tabs.js',
                    'js/templatemo-custom.js'
                ]
            }
        }
    
    def generate_asset_manifest(self) -> Dict[str, Dict]:
        """Generate manifest of all optimized assets with hashes"""
        manifest = {}
        
        for asset_type, bundles in self.bundles.items():
            manifest[asset_type] = {}
            
            for bundle_name, files in bundles.items():
                # Check if all files exist
                existing_files = []
                for file_path in files:
                    full_path = os.path.join(self.static_folder, file_path)
                    if os.path.exists(full_path):
                        existing_files.append(file_path)
                    else:
                        logger.warning(f"Asset file not found: {full_path}")
                
                if existing_files:
                    # Generate hash for bundle
                    bundle_hash = self._generate_bundle_hash(existing_files)
                    bundle_filename = f"{bundle_name}.{bundle_hash[:8]}.{asset_type}"
                    
                    manifest[asset_type][bundle_name] = {
                        'files': existing_files,
                        'bundle': bundle_filename,
                        'hash': bundle_hash,
                        'size_kb': self._calculate_bundle_size(existing_files)
                    }
        
        # Save manifest to file
        try:
            with open(self.manifest_file, 'w') as f:
                json.dump(manifest, f, indent=2)
            logger.info(f"Asset manifest generated: {self.manifest_file}")
        except Exception as e:
            logger.error(f"Failed to save asset manifest: {e}")
        
        return manifest
    
    def _generate_bundle_hash(self, files: List[str]) -> str:
        """Generate hash for a bundle of files based on their content"""
        hasher = hashlib.md5()
        
        for file_path in sorted(files):  # Sort for consistent hashing
            full_path = os.path.join(self.static_folder, file_path)
            try:
                with open(full_path, 'rb') as f:
                    hasher.update(f.read())
            except Exception as e:
                logger.warning(f"Could not read file for hashing: {full_path} - {e}")
        
        return hasher.hexdigest()
    
    def _calculate_bundle_size(self, files: List[str]) -> float:
        """Calculate total size of bundle in KB"""
        total_size = 0
        
        for file_path in files:
            full_path = os.path.join(self.static_folder, file_path)
            try:
                total_size += os.path.getsize(full_path)
            except Exception as e:
                logger.warning(f"Could not get size for file: {full_path} - {e}")
        
        return round(total_size / 1024, 2)  # Convert to KB
    
    def create_bundle(self, asset_type: str, bundle_name: str, output_dir: str = None) -> Optional[str]:
        """Create a bundled and minified asset file"""
        if asset_type not in self.bundles or bundle_name not in self.bundles[asset_type]:
            logger.error(f"Bundle not found: {asset_type}/{bundle_name}")
            return None
        
        files = self.bundles[asset_type][bundle_name]
        bundle_hash = self._generate_bundle_hash(files)
        bundle_filename = f"{bundle_name}.{bundle_hash[:8]}.{asset_type}"
        
        output_dir = output_dir or os.path.join(self.static_folder, 'bundles')
        os.makedirs(output_dir, exist_ok=True)
        
        bundle_path = os.path.join(output_dir, bundle_filename)
        
        # Skip if bundle already exists
        if os.path.exists(bundle_path):
            logger.info(f"Bundle already exists: {bundle_filename}")
            return bundle_filename
        
        try:
            with open(bundle_path, 'w') as bundle_file:
                # Add bundle header
                bundle_file.write(f"/* ChosyTable {asset_type.upper()} Bundle: {bundle_name} */\n")
                bundle_file.write(f"/* Generated: {datetime.now().isoformat()} */\n\n")
                
                for file_path in files:
                    full_path = os.path.join(self.static_folder, file_path)
                    try:
                        with open(full_path, 'r') as f:
                            content = f.read()
                            
                            # Add file separator
                            bundle_file.write(f"/* === {file_path} === */\n")
                            bundle_file.write(content)
                            bundle_file.write("\n\n")
                            
                    except Exception as e:
                        logger.error(f"Failed to read file {full_path}: {e}")
                        continue
            
            logger.info(f"Bundle created: {bundle_filename} ({self._calculate_bundle_size([bundle_path]):.2f}KB)")
            return bundle_filename
            
        except Exception as e:
            logger.error(f"Failed to create bundle {bundle_filename}: {e}")
            return None
    
    def get_bundle_url(self, asset_type: str, bundle_name: str) -> str:
        """Get URL for bundled asset, creating it if necessary"""
        try:
            # Try to load existing manifest
            if os.path.exists(self.manifest_file):
                with open(self.manifest_file, 'r') as f:
                    manifest = json.load(f)
                
                if (asset_type in manifest and 
                    bundle_name in manifest[asset_type]):
                    bundle_filename = manifest[asset_type][bundle_name]['bundle']
                    return url_for('static', filename=f'bundles/{bundle_filename}')
            
            # Create bundle if not found
            bundle_filename = self.create_bundle(asset_type, bundle_name)
            if bundle_filename:
                return url_for('static', filename=f'bundles/{bundle_filename}')
                
        except Exception as e:
            logger.error(f"Failed to get bundle URL: {e}")
        
        # Fallback to individual files
        return self._get_fallback_urls(asset_type, bundle_name)
    
    def _get_fallback_urls(self, asset_type: str, bundle_name: str) -> List[str]:
        """Get individual file URLs as fallback"""
        if (asset_type not in self.bundles or 
            bundle_name not in self.bundles[asset_type]):
            return []
        
        urls = []
        for file_path in self.bundles[asset_type][bundle_name]:
            full_path = os.path.join(self.static_folder, file_path)
            if os.path.exists(full_path):
                urls.append(url_for('static', filename=file_path))
        
        return urls
    
    def cleanup_old_bundles(self, keep_count: int = 3):
        """Clean up old bundle files, keeping only the most recent versions"""
        bundles_dir = os.path.join(self.static_folder, 'bundles')
        
        if not os.path.exists(bundles_dir):
            return
        
        # Group files by bundle name (without hash)
        bundle_groups = {}
        
        for filename in os.listdir(bundles_dir):
            if '.' in filename:
                # Extract bundle name (everything before first hash-like segment)
                parts = filename.split('.')
                if len(parts) >= 3:  # name.hash.ext
                    bundle_name = parts[0]
                    if bundle_name not in bundle_groups:
                        bundle_groups[bundle_name] = []
                    
                    file_path = os.path.join(bundles_dir, filename)
                    mtime = os.path.getmtime(file_path)
                    bundle_groups[bundle_name].append((filename, mtime))
        
        # Clean up old files
        for bundle_name, files in bundle_groups.items():
            if len(files) > keep_count:
                # Sort by modification time (newest first)
                files.sort(key=lambda x: x[1], reverse=True)
                
                # Remove old files
                for filename, _ in files[keep_count:]:
                    file_path = os.path.join(bundles_dir, filename)
                    try:
                        os.remove(file_path)
                        logger.info(f"Removed old bundle: {filename}")
                    except Exception as e:
                        logger.error(f"Failed to remove old bundle {filename}: {e}")

# Template helper functions
def get_css_bundle_url(bundle_name: str = 'core') -> str:
    """Template helper to get CSS bundle URL"""
    optimizer = AssetOptimizer()
    return optimizer.get_bundle_url('css', bundle_name)

def get_js_bundle_url(bundle_name: str = 'core') -> str:
    """Template helper to get JS bundle URL"""
    optimizer = AssetOptimizer()
    return optimizer.get_bundle_url('js', bundle_name)

# Global asset optimizer
asset_optimizer = AssetOptimizer()