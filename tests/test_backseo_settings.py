"""Unit tests for BackSEOSettings module."""
import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from BackSEOSettings import BackSEOSettings, user_settings_dir, user_local_dir


class TestUserDirectoryFunctions:
    """Tests for user directory utility functions."""

    def test_user_settings_dir_returns_path(self):
        """Test that user_settings_dir returns a Path object."""
        result = user_settings_dir()
        assert isinstance(result, Path)
        assert "Back SEO Marketing Software" in str(result)

    def test_user_local_dir_returns_path(self):
        """Test that user_local_dir returns a Path object."""
        result = user_local_dir()
        assert isinstance(result, Path)
        assert "Back SEO Marketing Software" in str(result)

    @patch('platform.system')
    def test_user_settings_dir_windows(self, mock_system):
        """Test user_settings_dir returns correct path for Windows."""
        mock_system.return_value = "Windows"
        result = user_settings_dir()
        assert "AppData" in str(result)
        assert "Local" in str(result)

    @patch('platform.system')
    def test_user_settings_dir_mac(self, mock_system):
        """Test user_settings_dir returns correct path for Mac."""
        mock_system.return_value = "Darwin"
        result = user_settings_dir()
        assert "Library" in str(result)
        assert "Caches" in str(result)

    @patch('platform.system')
    def test_user_settings_dir_linux(self, mock_system):
        """Test user_settings_dir returns correct path for Linux."""
        mock_system.return_value = "Linux"
        result = user_settings_dir()
        assert ".cache" in str(result)


class TestBackSEOSettings:
    """Tests for BackSEOSettings class."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Set up test fixtures and clean up after tests."""
        # Clear singleton instance before each test
        BackSEOSettings._instances.clear()
        
        # Create temporary directory for test outputs
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        yield
        
        # Clean up after test
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_settings_creates_output_directories(self):
        """Test that BackSEOSettings creates necessary output directories."""
        settings = BackSEOSettings()
        
        # Check that output directories are created
        expected_dirs = [
            "output/custom",
            "output/htmls",
            "output/images",
            "output/localclients",
            "output/reports",
            "output/screenshots",
            "output/search_results_audit",
            "output/sitemap_audits",
            "Plugins",
        ]
        
        for dir_path in expected_dirs:
            assert os.path.exists(dir_path), f"Directory {dir_path} should exist"

    def test_settings_default_values(self):
        """Test that BackSEOSettings initializes with correct default values."""
        settings = BackSEOSettings()
        
        assert settings.vsync is True
        assert settings.animations is True
        assert settings.fps == 120
        assert settings.width == 1280
        assert settings.height == 800
        assert settings.agencyOutput == "output"
        assert settings.helperthreads == 4

    def test_settings_cpu_cores_reasonable(self):
        """Test that CPU cores settings are reasonable."""
        settings = BackSEOSettings()
        
        import multiprocessing
        cpu_count = multiprocessing.cpu_count()
        
        assert settings.cpucores == cpu_count / 2
        assert settings.maxcpucores == cpu_count
        assert settings.cpucores > 0
        assert settings.maxcpucores > 0

    def test_settings_singleton_pattern(self):
        """Test that BackSEOSettings follows singleton pattern."""
        settings1 = BackSEOSettings()
        settings2 = BackSEOSettings()
        
        assert settings1 is settings2, "BackSEOSettings should be a singleton"

    def test_settings_file_path_created(self):
        """Test that settings file path is properly set."""
        settings = BackSEOSettings()
        
        assert isinstance(settings.settingsOutpath, Path)
        assert isinstance(settings.settingsFile, Path)
        assert settings.settingsFile.name == "settings.bseo"

    def test_change_vsync(self):
        """Test changing vsync setting."""
        settings = BackSEOSettings()
        
        settings.changeVsync(False)
        assert settings.vsync is False
        
        settings.changeVsync(True)
        assert settings.vsync is True

    def test_set_viewport(self):
        """Test setting viewport."""
        settings = BackSEOSettings()
        mock_viewport = MagicMock()
        
        settings.setVp(mock_viewport)
        assert settings.vp is mock_viewport


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
