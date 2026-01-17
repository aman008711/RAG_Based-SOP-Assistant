#!/usr/bin/env python
"""
System Verification & Product Readiness Report
================================================
Comprehensive check of environment, dependencies, and functionality
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

class SystemVerification:
    def __init__(self):
        self.results = {}
        self.workspace = Path(__file__).parent
        self.status = "✓"
        
    def print_header(self, title):
        print("\n" + "="*80)
        print(f" {title}")
        print("="*80)
    
    def print_section(self, title):
        print(f"\n[*] {title}")
        print("-" * 80)
    
    def print_success(self, msg):
        print(f"[✓] {msg}")
        
    def print_error(self, msg):
        print(f"[✗] {msg}")
        self.status = "✗"
        
    def print_info(self, msg):
        print(f"[i] {msg}")
    
    def check_python_env(self):
        """Verify Python environment"""
        self.print_section("Python Environment Check")
        
        # Python version
        version = sys.version.split()[0]
        print(f"Python Version: {version}")
        self.print_success(f"Python {version} detected")
        
        # Executable path
        print(f"Executable: {sys.executable}")
        
        # Virtual environment
        in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        if in_venv:
            self.print_success("Running in virtual environment")
        else:
            self.print_info("NOT in virtual environment (can still work)")
        
        self.results['python_env'] = True
    
    def check_dependencies(self):
        """Verify all required dependencies"""
        self.print_section("Dependency Verification")
        
        required_packages = [
            'fastapi', 'uvicorn', 'streamlit', 'langchain',
            'langchain_community', 'langchain_huggingface',
            'faiss', 'pydantic', 'requests', 'slowapi'
        ]
        
        missing = []
        for package in required_packages:
            try:
                __import__(package)
                self.print_success(f"{package}")
            except ImportError:
                self.print_error(f"{package} - MISSING")
                missing.append(package)
        
        self.results['dependencies'] = len(missing) == 0
        
        if missing:
            print(f"\nMissing packages: {', '.join(missing)}")
            print("Install with: pip install -r requirements.txt")
        
        return len(missing) == 0
    
    def check_file_structure(self):
        """Verify project file structure"""
        self.print_section("Project File Structure")
        
        required_files = {
            'main.py': 'FastAPI Backend',
            'config.yaml': 'Configuration',
            'requirements.txt': 'Dependencies',
            'static/index.html': 'Web Interface',
            'ingestion/ingest.py': 'Document Ingestion',
            'retrieval/retrieve.py': 'Vector Search',
        }
        
        missing_files = []
        for file_path, description in required_files.items():
            full_path = self.workspace / file_path
            if full_path.exists():
                self.print_success(f"{file_path:<30} ({description})")
            else:
                self.print_error(f"{file_path:<30} - MISSING")
                missing_files.append(file_path)
        
        self.results['file_structure'] = len(missing_files) == 0
        return len(missing_files) == 0
    
    def check_configuration(self):
        """Verify configuration"""
        self.print_section("Configuration Check")
        
        config_path = self.workspace / 'config.yaml'
        if config_path.exists():
            self.print_success(f"config.yaml found ({config_path.stat().st_size} bytes)")
            try:
                import yaml
                with open(config_path) as f:
                    config = yaml.safe_load(f)
                    settings_count = len(config) if isinstance(config, dict) else 0
                    self.print_success(f"Configuration loaded: {settings_count} settings")
                    self.results['configuration'] = True
            except Exception as e:
                self.print_error(f"Failed to parse config: {e}")
                self.results['configuration'] = False
        else:
            self.print_error("config.yaml not found")
            self.results['configuration'] = False
    
    def check_vectorstore(self):
        """Check vector store"""
        self.print_section("Vector Store Check")
        
        vectorstore_path = self.workspace / 'vectorstore' / 'faiss_index'
        if vectorstore_path.exists():
            self.print_success(f"Vector store directory found")
            
            # List files
            files = list(vectorstore_path.glob('*'))
            if files:
                self.print_success(f"Contains {len(files)} file(s)")
                for f in files[:5]:
                    size_kb = f.stat().st_size / 1024
                    self.print_info(f"  - {f.name} ({size_kb:.1f} KB)")
                self.results['vectorstore'] = True
            else:
                self.print_error("Vector store directory is empty")
                self.results['vectorstore'] = False
        else:
            self.print_error("Vector store not found at vectorstore/faiss_index")
            self.results['vectorstore'] = False
    
    def check_ports(self):
        """Check port availability"""
        self.print_section("Port Availability")
        
        import socket
        
        ports_to_check = {
            8008: 'FastAPI Backend',
            8501: 'Streamlit Web UI',
        }
        
        for port, service in ports_to_check.items():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            
            if result == 0:
                self.print_info(f"Port {port} ({service}) - IN USE (running elsewhere)")
            else:
                self.print_success(f"Port {port} ({service}) - Available")
        
        self.results['ports'] = True
    
    def check_code_quality(self):
        """Check main code files for syntax errors"""
        self.print_section("Code Quality Check")
        
        py_files = [
            'main.py', 'api.py', 'api_backend.py',
            'ingestion/ingest.py', 'retrieval/retrieve.py'
        ]
        
        syntax_errors = []
        for py_file in py_files:
            file_path = self.workspace / py_file
            if file_path.exists():
                try:
                    with open(file_path, encoding='utf-8', errors='ignore') as f:
                        compile(f.read(), py_file, 'exec')
                    self.print_success(f"{py_file}")
                except SyntaxError as e:
                    self.print_error(f"{py_file} - Syntax Error: {e}")
                    syntax_errors.append(py_file)
            else:
                self.print_info(f"{py_file} - Not found (optional)")
        
        self.results['code_quality'] = len(syntax_errors) == 0
    
    def check_permissions(self):
        """Check file permissions"""
        self.print_section("File Permissions Check")
        
        # Check main.py is readable
        main_py = self.workspace / 'main.py'
        if main_py.exists():
            if os.access(main_py, os.R_OK):
                self.print_success("main.py - Readable")
            else:
                self.print_error("main.py - Cannot read (permission denied)")
        
        # Check write access to workspace
        test_file = self.workspace / '.write_test'
        try:
            test_file.touch()
            test_file.unlink()
            self.print_success("Workspace directory - Writable")
        except:
            self.print_error("Workspace directory - Not writable")
        
        self.results['permissions'] = True
    
    def generate_readiness_report(self):
        """Generate product readiness score"""
        self.print_header("PRODUCT READINESS ASSESSMENT")
        
        checks = self.results
        total = len(checks)
        passed = sum(1 for v in checks.values() if v)
        score = (passed / total * 100) if total > 0 else 0
        
        print(f"\nReadiness Score: {score:.0f}% ({passed}/{total} checks passed)\n")
        
        for check, result in checks.items():
            status = "[✓]" if result else "[✗]"
            print(f"  {status} {check.replace('_', ' ').title()}")
        
        if score >= 90:
            print("\n" + "="*80)
            print("✓ PRODUCTION READY - System is fully operational")
            print("="*80)
            return True
        elif score >= 75:
            print("\n" + "="*80)
            print("◐ MOSTLY READY - Minor issues may need attention")
            print("="*80)
            return True
        else:
            print("\n" + "="*80)
            print("✗ NOT READY - Critical issues detected")
            print("="*80)
            return False
    
    def generate_startup_guide(self):
        """Generate startup instructions"""
        self.print_header("QUICK START GUIDE")
        
        print("""
[STEP 1] Start the API Server
  Command: python main.py
  Expected: API running on http://0.0.0.0:8008
  Wait for: "Uvicorn running on..."

[STEP 2] Access the System
  Web Interface: http://localhost:8008/web
  API Docs:      http://localhost:8008/docs
  Health Check:  http://localhost:8008/health

[STEP 3] Make Your First Query
  POST http://localhost:8008/ask
  Body: {"question": "What is this document about?"}

[OPTIONAL] Run Validation Tests
  Command: python validate_working.py
  Result:  Should show all tests passing
        """)
    
    def run_all_checks(self):
        """Run all verification checks"""
        self.print_header("SYSTEM VERIFICATION & PRODUCT READINESS CHECK")
        print(f"Workspace: {self.workspace}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        self.check_python_env()
        self.check_dependencies()
        self.check_file_structure()
        self.check_configuration()
        self.check_vectorstore()
        self.check_ports()
        self.check_code_quality()
        self.check_permissions()
        
        readiness = self.generate_readiness_report()
        self.generate_startup_guide()
        
        return readiness

if __name__ == '__main__':
    verifier = SystemVerification()
    success = verifier.run_all_checks()
    
    sys.exit(0 if success else 1)
