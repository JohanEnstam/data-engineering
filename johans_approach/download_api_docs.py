#!/usr/bin/env python3
"""
Download API Documentation Script
Downloads HTML documentation from SMHI and Trafiklab API pages
"""
import requests
import os
from datetime import datetime
import json

def download_html(url, filename, description):
    """Download HTML content from URL"""
    try:
        print(f"Downloading {description} from {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Save HTML content
        os.makedirs('api_documentation', exist_ok=True)
        filepath = f"api_documentation/{filename}"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"✅ Saved {description} to {filepath}")
        return {
            'success': True,
            'url': url,
            'filename': filepath,
            'size': len(response.text),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Failed to download {description}: {e}")
        return {
            'success': False,
            'url': url,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

def main():
    """Download API documentation from various sources"""
    print("🔍 DOWNLOADING API DOCUMENTATION")
    print("="*50)
    
    # API documentation URLs to download
    api_docs = [
        {
            'url': 'https://opendata.smhi.se/apidocs/',
            'filename': 'smhi_api_docs.html',
            'description': 'SMHI API Documentation'
        },
        {
            'url': 'https://www.trafiklab.se/api',
            'filename': 'trafiklab_api_docs.html',
            'description': 'Trafiklab API Documentation'
        },
        {
            'url': 'https://www.trafiklab.se/api/gtfs',
            'filename': 'trafiklab_gtfs_docs.html',
            'description': 'Trafiklab GTFS Documentation'
        },
        {
            'url': 'https://opendata.smhi.se/ws/rest/',
            'filename': 'smhi_observations_api.html',
            'description': 'SMHI Observations API'
        },
        {
            'url': 'https://opendata-download-metfcst.smhi.se/api/',
            'filename': 'smhi_forecast_api.html',
            'description': 'SMHI Forecast API'
        },
        {
            'url': 'https://api.sl.se/api2/',
            'filename': 'sl_api_docs.html',
            'description': 'SL API Documentation'
        }
    ]
    
    results = []
    
    for doc in api_docs:
        result = download_html(doc['url'], doc['filename'], doc['description'])
        results.append({
            'description': doc['description'],
            'result': result
        })
    
    # Save summary
    summary = {
        'timestamp': datetime.now().isoformat(),
        'total_docs': len(api_docs),
        'successful_downloads': len([r for r in results if r['result']['success']]),
        'failed_downloads': len([r for r in results if not r['result']['success']]),
        'results': results
    }
    
    with open('api_documentation/download_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*50)
    print("📊 DOWNLOAD SUMMARY")
    print("="*50)
    print(f"Total documents: {summary['total_docs']}")
    print(f"Successful: {summary['successful_downloads']}")
    print(f"Failed: {summary['failed_downloads']}")
    print(f"Summary saved to: api_documentation/download_summary.json")
    
    # Show failed downloads
    failed = [r for r in results if not r['result']['success']]
    if failed:
        print("\n❌ Failed downloads:")
        for f in failed:
            print(f"  • {f['description']}: {f['result']['error']}")

if __name__ == "__main__":
    main()
