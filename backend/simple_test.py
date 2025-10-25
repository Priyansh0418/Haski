#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple test to identify the exact issue
"""
import sys
import os
import traceback
from pathlib import Path

# Ensure we work with an absolute resolved project path
BASE_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(BASE_DIR))
os.chdir(str(BASE_DIR))

print("Starting app test...")

def _safe_response_repr(resp):
	"""Return JSON if possible, otherwise plain text."""
	try:
		return resp.json()
	except Exception:
		try:
			return resp.text
		except Exception:
			return "<unable to decode response>"

def main():
	try:
		from app.main import app
		from fastapi.testclient import TestClient

		# Use TestClient as a context manager to ensure proper cleanup
		with TestClient(app) as client:
			print("Testing GET /")
			resp = client.get("/")
			print(f"GET / => {resp.status_code}")
			print(f"Response: {_safe_response_repr(resp)}")

			print("\nTesting POST /api/v1/auth/login")
			resp = client.post("/api/v1/auth/login", json={
				"email": "demo@haski.com",
				"password": "Demo@123"
			})
			print(f"POST /api/v1/auth/login => {resp.status_code}")
			print(f"Response: {_safe_response_repr(resp)}")

	except Exception as e:
		print(f"ERROR: {e}")
		traceback.print_exc()
		# Non-zero exit to indicate failure to CI/tools
		sys.exit(1)

	print("Test complete.")

if __name__ == "__main__":
	main()
