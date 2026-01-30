#!/usr/bin/env python3
"""
Test runner for FHIR SDK test suite.

This script runs all tests and provides a summary report.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_tests(test_path=None, verbose=False, coverage=False):
    """Run the test suite with optional parameters."""
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add test path if specified
    if test_path:
        cmd.append(test_path)
    else:
        cmd.append("tests/")
    
    # Add verbose flag
    if verbose:
        cmd.append("-v")
    
    # Add coverage if requested
    if coverage:
        cmd.extend(["--cov=fhir_sdk", "--cov-report=html", "--cov-report=term"])
    
    # Add other useful flags
    cmd.extend([
        "--tb=short",  # Shorter traceback format
        "--strict-markers",  # Strict marker handling
        "-x"  # Stop on first failure
    ])
    
    print(f"Running: {' '.join(cmd)}")
    print("-" * 80)
    
    try:
        result = subprocess.run(cmd, check=True, cwd=Path(__file__).parent.parent)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"Tests failed with return code: {e.returncode}")
        return e.returncode
    except FileNotFoundError:
        print("Error: pytest not found. Please install pytest:")
        print("pip install pytest pytest-cov")
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run FHIR SDK tests")
    parser.add_argument("test_path", nargs="?", help="Specific test file or directory to run")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-c", "--coverage", action="store_true", help="Run with coverage report")
    parser.add_argument("--install-deps", action="store_true", help="Install test dependencies")
    
    args = parser.parse_args()
    
    if args.install_deps:
        print("Installing test dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest", "pytest-cov"], check=True)
        print("Dependencies installed successfully!")
        return 0
    
    return run_tests(args.test_path, args.verbose, args.coverage)


if __name__ == "__main__":
    sys.exit(main())
