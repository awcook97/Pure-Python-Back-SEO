"""Unit tests for BackSEODataHandler module."""
import pytest
import json
import os
import tempfile
import shutil
from multiprocessing import Queue

# Skip all tests if dearpygui is not installed
pytest.importorskip("dearpygui", reason="dearpygui not installed")

from BackSEODataHandler import BackSEODataHandler, getBackSEODataHandler


class TestBackSEODataHandler:
    """Tests for BackSEODataHandler class."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Set up test fixtures and clean up after tests."""
        # Create temporary directory for test outputs
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create queues for testing
        self.job_queue = Queue()
        self.results_queue = Queue()
        
        yield
        
        # Clean up after test
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_data_handler_initialization(self):
        """Test that BackSEODataHandler initializes correctly."""
        handler = BackSEODataHandler(self.job_queue, self.results_queue)
        
        assert handler.job_queue is self.job_queue
        assert handler.results_queue is self.results_queue
        assert handler.updateall is False
        assert handler.updateMessage == ("", "")
        assert isinstance(handler.localReports, dict)
        assert isinstance(handler.searchReports, dict)
        assert isinstance(handler.siteAuditReports, dict)
        assert isinstance(handler.bseoObjects, dict)
        assert isinstance(handler.bseoSaveObjects, dict)

    def test_add_object_without_save_state(self):
        """Test adding an object without save state."""
        handler = BackSEODataHandler(self.job_queue, self.results_queue)
        test_obj = {"test": "data"}
        
        handler.add_object(test_obj, "test_object", saveState=False)
        
        assert "test_object" in handler.bseoObjects
        assert handler.bseoObjects["test_object"] is test_obj
        assert "test_object" not in handler.bseoSaveObjects

    def test_add_object_with_save_state(self):
        """Test adding an object with save state."""
        handler = BackSEODataHandler(self.job_queue, self.results_queue)
        test_obj = {"test": "data"}
        
        handler.add_object(test_obj, "test_object", saveState=True)
        
        assert "test_object" in handler.bseoSaveObjects
        assert handler.bseoSaveObjects["test_object"] is test_obj
        assert "test_object" not in handler.bseoObjects

    def test_save_data_creates_file(self):
        """Test that save_data creates a data file."""
        handler = BackSEODataHandler(self.job_queue, self.results_queue)
        handler.dataHolders = {}
        
        handler.saveData("category1", "key1", "value1")
        
        assert os.path.exists("bseodata")
        with open("bseodata", "r") as f:
            data = json.load(f)
        
        assert "category1" in data
        assert data["category1"]["key1"] == "value1"

    def test_save_data_updates_flag(self):
        """Test that save_data sets update flag."""
        handler = BackSEODataHandler(self.job_queue, self.results_queue)
        handler.dataHolders = {}
        
        handler.saveData("category1", "key1", "value1")
        
        assert handler.updateall is True
        assert handler.updateMessage == ("fileupdate", "value1")

    def test_savenoupdate_does_not_set_flag(self):
        """Test that savenoupdate does not set update flag."""
        handler = BackSEODataHandler(self.job_queue, self.results_queue)
        handler.dataHolders = {}
        
        handler.savenoupdate("category1", "key1", "value1")
        
        assert handler.updateall is False
        assert os.path.exists("bseodata")

    def test_finished_updates(self):
        """Test that finishedUpdates resets update flag."""
        handler = BackSEODataHandler(self.job_queue, self.results_queue)
        handler.updateall = True
        
        handler.finishedUpdates()
        
        assert handler.updateall is False

    def test_load_returns_empty_dict_when_no_file(self):
        """Test that load returns empty dict when no data file exists."""
        handler = BackSEODataHandler(self.job_queue, self.results_queue)
        
        result = handler.load()
        
        assert result == {}

    def test_load_returns_data_when_file_exists(self):
        """Test that load returns data when file exists."""
        handler = BackSEODataHandler(self.job_queue, self.results_queue)
        
        # Create test data file
        test_data = {"category": {"key": "value"}}
        with open("bseodata", "w") as f:
            json.dump(test_data, f)
        
        result = handler.load()
        
        assert result == test_data

    def test_loaddata_returns_none_for_missing_category(self):
        """Test that loaddata returns None for missing category."""
        handler = BackSEODataHandler(self.job_queue, self.results_queue)
        handler.dataHolders = {}
        
        result = handler.loaddata("missing_category", "key")
        
        assert result is None
        assert "missing_category" in handler.dataHolders

    def test_loaddata_returns_none_for_missing_key(self):
        """Test that loaddata returns None for missing key."""
        handler = BackSEODataHandler(self.job_queue, self.results_queue)
        handler.dataHolders = {"category": {}}
        
        result = handler.loaddata("category", "missing_key")
        
        assert result is None
        assert "missing_key" in handler.dataHolders["category"]

    def test_loaddata_returns_value_when_exists(self):
        """Test that loaddata returns value when it exists."""
        handler = BackSEODataHandler(self.job_queue, self.results_queue)
        handler.dataHolders = {"category": {"key": "test_value"}}
        
        result = handler.loaddata("category", "key")
        
        assert result == "test_value"


class TestGetBackSEODataHandler:
    """Tests for getBackSEODataHandler function."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Reset singleton state before each test."""
        # This would need access to the singleton pattern used in the module
        # For now, we'll just test that it returns an instance
        yield

    def test_get_back_seo_data_handler_returns_instance(self):
        """Test that getBackSEODataHandler returns a BackSEODataHandler instance."""
        handler = getBackSEODataHandler()
        
        assert isinstance(handler, BackSEODataHandler)

    def test_get_back_seo_data_handler_returns_same_instance(self):
        """Test that getBackSEODataHandler returns the same instance (singleton)."""
        handler1 = getBackSEODataHandler()
        handler2 = getBackSEODataHandler()
        
        assert handler1 is handler2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
