#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-05 12:50:00 (ywatanabe)"

"""
Test runner for SciTex
"""

import unittest
import argparse
import sys
import os
import glob

def run_tests(test_pattern="test_*.py", verbosity=1, failfast=False):
    """
    Run tests matching the given pattern.
    
    Args:
        test_pattern: Pattern to match test files
        verbosity: Verbosity level for test output
        failfast: Whether to stop on first failure
        
    Returns:
        True if all tests pass, False otherwise
    """
    print(f"Running tests matching pattern: {test_pattern}")
    
    # Discover and run tests
    loader = unittest.TestLoader()
    
    if os.path.exists(test_pattern) and os.path.isfile(test_pattern):
        # Run a specific test file
        test_dir = os.path.dirname(test_pattern)
        pattern = os.path.basename(test_pattern)
        suite = loader.discover(test_dir, pattern=pattern)
    else:
        # Run tests matching the pattern
        suite = loader.discover("tests", pattern=test_pattern)
    
    runner = unittest.TextTestRunner(verbosity=verbosity, failfast=failfast)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def list_tests():
    """
    List available test files.
    
    Returns:
        A list of test file paths
    """
    test_files = []
    
    # Find all test files in tests directory
    for root, _, _ in os.walk("tests"):
        test_files.extend(glob.glob(os.path.join(root, "test_*.py")))
    
    # Sort test files
    test_files.sort()
    
    return test_files

def main():
    """Main entry point for test runner."""
    parser = argparse.ArgumentParser(description="Run SciTex tests")
    parser.add_argument(
        "--pattern", "-p",
        default="test_*.py",
        help="Pattern to match test files"
    )
    parser.add_argument(
        "--verbosity", "-v",
        type=int,
        default=1,
        choices=[0, 1, 2],
        help="Verbosity level (0-2)"
    )
    parser.add_argument(
        "--failfast", "-f",
        action="store_true",
        help="Stop on first failure"
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List available tests"
    )
    
    args = parser.parse_args()
    
    if args.list:
        print("Available tests:")
        for test_file in list_tests():
            print(f"  {test_file}")
        return 0
    
    # Run tests
    success = run_tests(
        test_pattern=args.pattern,
        verbosity=args.verbosity,
        failfast=args.failfast
    )
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())