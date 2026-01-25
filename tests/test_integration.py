"""Integration tests for Pure Python Back SEO."""
import pytest
import os
import sys

# Add project root to path to ensure imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestProjectStructure:
    """Test that the project structure is correct."""

    def test_main_modules_exist(self):
        """Test that main modules exist."""
        modules = [
            "BackSEOAgencies.py",
            "BackSEOSettings.py",
            "BackSEODataHandler.py",
            "BackSEOApplicationManager.py",
            "PluginController.py",
            "FlaskApp.py",
            "core.py",
            "__main__.py",
        ]
        
        for module in modules:
            assert os.path.exists(module), f"Module {module} should exist"

    def test_directories_exist(self):
        """Test that important directories exist."""
        directories = [
            "SEO",
            "Utils",
            "Plugins",
            "core_ui",
            "templates",
            "static",
        ]
        
        for directory in directories:
            assert os.path.exists(directory), f"Directory {directory} should exist"

    def test_config_files_exist(self):
        """Test that configuration files exist."""
        files = [
            "pyproject.toml",
            "requirements.txt",
            ".python-version",
            "README.md",
            "LICENSE",
        ]
        
        for file in files:
            assert os.path.exists(file), f"File {file} should exist"

    def test_python_version_file_content(self):
        """Test that .python-version has correct version."""
        with open(".python-version", "r") as f:
            version = f.read().strip()
        
        # Should be 3.13 or 3.12
        assert version in ["3.13", "3.12"], f"Python version should be 3.12 or 3.13, got {version}"

    def test_shebang_lines_correct(self):
        """Test that shebang lines are correct in executable scripts."""
        with open("BackSEOAgencies.py", "r") as f:
            first_line = f.readline().strip()
        
        # Should be portable shebang
        assert first_line == "#!/usr/bin/env python3", \
            f"Shebang should be '#!/usr/bin/env python3', got '{first_line}'"


class TestImports:
    """Test that key modules can be imported."""

    def test_import_backseo_settings(self):
        """Test that BackSEOSettings can be imported."""
        pytest.importorskip("dearpygui", reason="dearpygui not installed")
        try:
            from BackSEOSettings import BackSEOSettings
            assert BackSEOSettings is not None
        except ImportError as e:
            pytest.fail(f"Failed to import BackSEOSettings: {e}")

    def test_import_backseo_datahandler(self):
        """Test that BackSEODataHandler can be imported."""
        pytest.importorskip("dearpygui", reason="dearpygui not installed")
        try:
            from BackSEODataHandler import BackSEODataHandler
            assert BackSEODataHandler is not None
        except ImportError as e:
            pytest.fail(f"Failed to import BackSEODataHandler: {e}")

    def test_import_plugin_controller(self):
        """Test that PluginController can be imported."""
        pytest.importorskip("dearpygui", reason="dearpygui not installed")
        try:
            from PluginController import PluginController
            assert PluginController is not None
        except ImportError as e:
            pytest.fail(f"Failed to import PluginController: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
