#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validate DOIs in scitex.scholar library by checking accessibility at https://doi.org/<DOI>
"""

import sys
import json
import time
from pathlib import Path
import requests
from typing import Dict, List, Tuple

sys.path.insert(0, str(Path.home() / "proj/scitex-code/src"))

from scitex import logging

logger = logging.getLogger(__name__)


def check_doi_accessible(doi: str, timeout: int = 10) -> Tuple[bool, str, int]:
    """Check if DOI is accessible at https://doi.org/<DOI>.

    Args:
        doi: DOI string (e.g., "10.1038/s41598-023-12345-6")
        timeout: Request timeout in seconds

    Returns:
        Tuple of (is_valid, message, status_code)
    """
    if not doi:
        return False, "Empty DOI", 0

    # Clean DOI (remove https://doi.org/ prefix if present)
    doi_clean = doi.replace("https://doi.org/", "").replace("http://dx.doi.org/", "")

    url = f"https://doi.org/{doi_clean}"

    try:
        # Use HEAD request first (faster, less data)
        response = requests.head(
            url,
            timeout=timeout,
            allow_redirects=True,
            headers={'User-Agent': 'SciTeX-Scholar/1.0 (DOI Validator)'}
        )

        # DOI service returns 404 for invalid DOIs
        if response.status_code == 404:
            return False, "DOI Not Found (404)", 404

        # Some publishers don't support HEAD, try GET
        if response.status_code == 405:  # Method Not Allowed
            response = requests.get(
                url,
                timeout=timeout,
                allow_redirects=True,
                headers={'User-Agent': 'SciTeX-Scholar/1.0 (DOI Validator)'}
            )

        # Success codes (200-399, including redirects)
        if 200 <= response.status_code < 400:
            # Check if we got redirected to publisher
            if response.url != url:
                return True, f"Valid (redirected to {response.url[:50]}...)", response.status_code
            return True, "Valid (resolved)", response.status_code

        return False, f"HTTP {response.status_code}", response.status_code

    except requests.exceptions.Timeout:
        return False, "Timeout", 0
    except requests.exceptions.ConnectionError:
        return False, "Connection Error", 0
    except Exception as e:
        return False, f"Error: {str(e)[:50]}", 0


def validate_library_dois(
    library_path: Path,
    delay_between_requests: float = 0.5,
    fix_invalid: bool = False
) -> Dict:
    """Validate all DOIs in the scholar library.

    Args:
        library_path: Path to MASTER directory
        delay_between_requests: Delay in seconds between DOI checks (be polite to DOI service)
        fix_invalid: If True, remove invalid DOIs from metadata.json files

    Returns:
        Dictionary with validation results
    """
    results = {
        'total_papers': 0,
        'papers_with_doi': 0,
        'valid_dois': 0,
        'invalid_dois': 0,
        'empty_dois': 0,
        'invalid_details': []
    }

    logger.info(f"Validating DOIs in: {library_path}")
    logger.info(f"Delay between requests: {delay_between_requests}s")

    # Find all metadata.json files
    metadata_files = list(library_path.glob("*/metadata.json"))
    results['total_papers'] = len(metadata_files)

    logger.info(f"Found {len(metadata_files)} papers to validate")

    print("\n" + "="*80)
    print("DOI VALIDATION REPORT")
    print("="*80)

    for i, metadata_file in enumerate(metadata_files, 1):
        paper_id = metadata_file.parent.name

        # Load metadata
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)

        doi = metadata.get('metadata', {}).get('id', {}).get('doi', '')
        title = metadata.get('metadata', {}).get('basic', {}).get('title', 'No title')[:60]

        if not doi:
            results['empty_dois'] += 1
            continue

        results['papers_with_doi'] += 1

        print(f"\n[{i}/{len(metadata_files)}] {title}...")
        print(f"  DOI: {doi}")

        # Check DOI accessibility
        is_valid, message, status_code = check_doi_accessible(doi)

        if is_valid:
            results['valid_dois'] += 1
            logger.success(f"  ✓ {message}")
        else:
            results['invalid_dois'] += 1
            logger.error(f"  ✗ {message}")

            results['invalid_details'].append({
                'paper_id': paper_id,
                'title': title,
                'doi': doi,
                'reason': message,
                'status_code': status_code,
                'metadata_file': str(metadata_file)
            })

            # Fix invalid DOI if requested
            if fix_invalid:
                logger.warning(f"  Removing invalid DOI from {metadata_file}")
                metadata['metadata']['id']['doi'] = ''
                metadata['metadata']['id']['doi_engines'] = []
                metadata['metadata']['url']['doi'] = None
                metadata['metadata']['url']['doi_engines'] = []

                with open(metadata_file, 'w') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)

                logger.info(f"  ✓ Removed invalid DOI from metadata")

        # Be polite to DOI service
        time.sleep(delay_between_requests)

    # Summary
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    print(f"Total papers: {results['total_papers']}")
    print(f"Papers with DOI: {results['papers_with_doi']}")
    print(f"  ✓ Valid DOIs: {results['valid_dois']} ({results['valid_dois']*100/max(results['papers_with_doi'],1):.1f}%)")
    print(f"  ✗ Invalid DOIs: {results['invalid_dois']} ({results['invalid_dois']*100/max(results['papers_with_doi'],1):.1f}%)")
    print(f"Papers without DOI: {results['empty_dois']}")

    # Invalid DOI details
    if results['invalid_details']:
        print("\n" + "="*80)
        print("INVALID DOI DETAILS")
        print("="*80)
        for item in results['invalid_details']:
            print(f"\n{item['title']}")
            print(f"  Paper ID: {item['paper_id']}")
            print(f"  DOI: {item['doi']}")
            print(f"  Reason: {item['reason']}")
            print(f"  File: {item['metadata_file']}")

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Validate DOIs in scitex.scholar library')
    parser.add_argument(
        '--library-path',
        type=Path,
        default=Path.home() / '.scitex/scholar/library/MASTER',
        help='Path to MASTER library directory'
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=0.5,
        help='Delay between DOI checks in seconds (default: 0.5)'
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Remove invalid DOIs from metadata.json files'
    )
    parser.add_argument(
        '--output',
        type=Path,
        help='Save validation report to JSON file'
    )

    args = parser.parse_args()

    # Validate DOIs
    results = validate_library_dois(
        library_path=args.library_path,
        delay_between_requests=args.delay,
        fix_invalid=args.fix
    )

    # Save results to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.success(f"\n✓ Validation results saved to: {args.output}")

    logger.success("\n✓ DOI validation complete!")
