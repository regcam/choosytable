#!/usr/bin/env python3
"""
Simple entry point for the Flask application.
Run with: python3 run.py
"""

from app import app

if __name__ == '__main__':
    app.run(debug=True)