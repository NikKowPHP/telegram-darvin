import importlib
import subprocess

def test_packages_installed():
    required_packages = [
        'qdrant_client',
        'sentence_transformers',
        'tree_sitter'
    ]
    
    missing = []
    for pkg in required_packages:
        try:
            importlib.import_module(pkg)
        except ImportError:
            missing.append(pkg)
    
    assert not missing, f"Missing required packages: {', '.join(missing)}"

def test_cct_command_available():
    result = subprocess.run(
        ['cct', '--help'],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, "cct command should exit with code 0 when called with --help"
    assert "usage" in result.stdout.lower(), "Help output should contain usage information"