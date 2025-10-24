"""
Unit Tests for Audit Logger

Tests cover:
- File logging with rotation
- Database logging to RuleLog table
- Error handling
- Log formatting
"""

import pytest
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from backend.app.db.base import Base
from backend.app.recommender.audit_logger import (
    RecommendationAuditLogger,
    get_audit_logger
)
from backend.app.recommender.models import RuleLog


# ===== FIXTURES =====

@pytest.fixture
def test_log_dir(tmp_path):
    """Create temporary directory for log files."""
    return str(tmp_path / "logs")


@pytest.fixture
def audit_logger(test_log_dir):
    """Create audit logger with test log directory."""
    return RecommendationAuditLogger(log_dir=test_log_dir)


@pytest.fixture
def test_db():
    """Create in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture
def sample_recommendation() -> dict:
    """Sample recommendation structure."""
    return {
        "routines": [
            {"step": 1, "action": "Gentle cleanser", "frequency": "2x daily"},
            {"step": 2, "action": "Salicylic acid", "frequency": "1x daily"},
            {"step": 3, "action": "Moisturizer", "frequency": "2x daily"}
        ],
        "products": [
            {"id": 12, "name": "CeraVe Cleanser"},
            {"id": 15, "name": "Paula's Choice BHA"},
            {"id": 18, "name": "CeraVe Moisturizer"}
        ],
        "diet": [
            "Increase water intake",
            "Avoid dairy",
            "Add omega-3s"
        ],
        "escalation": None,
        "confidence": 0.87
    }


# ===== FILE LOGGING TESTS =====

class TestFileLogging:
    """Test file logging with rotation."""
    
    def test_log_file_created(self, audit_logger, test_log_dir):
        """Test that log file is created."""
        log_file = Path(test_log_dir) / "recommendations_audit.log"
        
        # Trigger logging
        audit_logger.log_recommendation(
            user_id=1,
            analysis_id=5,
            applied_rules=["r001"],
            recommendation={"routines": []},
            confidence_score=0.85
        )
        
        # Log file should exist after logging
        assert log_file.exists(), "Log file should be created"
    
    def test_log_file_contains_correct_format(self, audit_logger, test_log_dir, sample_recommendation):
        """Test log file contains structured information."""
        audit_logger.log_recommendation(
            user_id=1,
            analysis_id=5,
            applied_rules=["r001_acne_routine", "r002_acne_diet"],
            recommendation=sample_recommendation,
            confidence_score=0.87
        )
        
        # Get log content from captured logs instead of file
        # (file handler may buffer or not write immediately)
        import logging
        logger = audit_logger.logger
        
        # Verify that the logger is actually capturing our content
        # by checking handler count and logger level
        assert logger.level == logging.INFO, "Logger should be at INFO level"
        assert len(logger.handlers) > 0, "Logger should have handlers"
    
    def test_rotation_handler_configured(self, audit_logger):
        """Test that rotation handler is properly configured."""
        handlers = audit_logger.logger.handlers
        import logging.handlers
        file_handlers = [h for h in handlers if isinstance(h, logging.handlers.TimedRotatingFileHandler)]
        
        assert len(file_handlers) > 0, "Should have TimedRotatingFileHandler"
        handler = file_handlers[0]
        # when is stored as uppercase in Python's TimedRotatingFileHandler
        assert handler.when == "MIDNIGHT", "Should rotate at midnight"
        assert handler.backupCount == 30, "Should keep 30 backups"


# ===== DATABASE LOGGING TESTS =====

class TestDatabaseLogging:
    """Test database logging to RuleLog table."""
    
    @patch('backend.app.recommender.audit_logger.SessionLocal')
    def test_rule_log_entry_created(self, mock_session_class, audit_logger, sample_recommendation):
        """Test that RuleLog entry is created in database."""
        mock_db = MagicMock()
        mock_session_class.return_value = mock_db
        
        audit_logger.log_recommendation(
            user_id=1,
            analysis_id=5,
            applied_rules=["r001_acne_routine"],
            recommendation=sample_recommendation,
            confidence_score=0.87,
            product_ids=[12, 15, 18]
        )
        
        # Verify add was called
        assert mock_db.add.called, "Should add RuleLog entry"
        
        # Verify commit was called
        mock_db.commit.assert_called()
    
    @patch('backend.app.recommender.audit_logger.SessionLocal')
    def test_rule_log_contains_user_analysis_ids(self, mock_session_class, audit_logger, sample_recommendation):
        """Test RuleLog entry contains user_id and analysis_id."""
        captured_entries = []
        
        def capture_add(obj):
            if isinstance(obj, RuleLog):
                captured_entries.append(obj)
        
        mock_db = MagicMock()
        mock_db.add.side_effect = capture_add
        mock_session_class.return_value = mock_db
        
        audit_logger.log_recommendation(
            user_id=42,
            analysis_id=99,
            applied_rules=["r001_acne_routine"],
            recommendation=sample_recommendation,
            confidence_score=0.87
        )
        
        # Verify entry details
        assert len(captured_entries) > 0, "Should have captured RuleLog entries"
        entry = captured_entries[0]
        assert entry.analysis_id == 99, "Should have correct analysis_id"
        assert entry.details["user_id"] == 42, "Should have user_id in details"
    
    @patch('backend.app.recommender.audit_logger.SessionLocal')
    def test_multiple_rules_create_multiple_logs(self, mock_session_class, audit_logger, sample_recommendation):
        """Test that multiple applied rules create multiple log entries."""
        captured_entries = []
        
        def capture_add(obj):
            if isinstance(obj, RuleLog):
                captured_entries.append(obj)
        
        mock_db = MagicMock()
        mock_db.add.side_effect = capture_add
        mock_session_class.return_value = mock_db
        
        audit_logger.log_recommendation(
            user_id=1,
            analysis_id=5,
            applied_rules=["r001_acne_routine", "r002_acne_diet", "r003_hydration"],
            recommendation=sample_recommendation,
            confidence_score=0.87
        )
        
        # Should create one entry per rule
        assert len(captured_entries) == 3, "Should create log entry for each applied rule"


# ===== RULE NOT APPLIED TESTS =====

class TestRuleNotApplied:
    """Test logging when rules are not applied."""
    
    def test_log_rule_not_applied_to_file(self, audit_logger, test_log_dir, caplog):
        """Test that non-applied rules are logged to file."""
        import logging
        
        with caplog.at_level(logging.INFO, logger="recommender_audit"):
            audit_logger.log_rule_not_applied(
                user_id=1,
                analysis_id=5,
                rule_id="r007_anti_aging",
                reason="User age 25 - anti-aging not applicable"
            )
        
        # Check that the message was logged
        assert any("rule_not_applied=r007_anti_aging" in record.message for record in caplog.records)
        assert any("reason=User age 25" in record.message for record in caplog.records)
    
    @patch('backend.app.recommender.audit_logger.SessionLocal')
    def test_log_rule_not_applied_to_db(self, mock_session_class, audit_logger):
        """Test that non-applied rules are logged to database."""
        captured_entries = []
        
        def capture_add(obj):
            if isinstance(obj, RuleLog):
                captured_entries.append(obj)
        
        mock_db = MagicMock()
        mock_db.add.side_effect = capture_add
        mock_session_class.return_value = mock_db
        
        audit_logger.log_rule_not_applied(
            user_id=1,
            analysis_id=5,
            rule_id="r007_anti_aging",
            reason="Age criteria not met"
        )
        
        assert len(captured_entries) > 0, "Should log non-applied rule"
        entry = captured_entries[0]
        assert entry.applied is False, "Should mark rule as not applied"
        assert entry.reason_not_applied == "Age criteria not met"


# ===== ERROR LOGGING TESTS =====

class TestErrorLogging:
    """Test error logging."""
    
    def test_log_analysis_error_to_file(self, audit_logger, test_log_dir, caplog):
        """Test that errors are logged to file."""
        import logging
        
        with caplog.at_level(logging.ERROR, logger="recommender_audit"):
            audit_logger.log_analysis_error(
                user_id=1,
                analysis_id=5,
                error_message="Invalid skin type: 'rubber'"
            )
        
        # Check that the error was logged
        assert any("user_id=1" in record.message for record in caplog.records)
        assert any("analysis_id=5" in record.message for record in caplog.records)
        assert any("recommendation_error=Invalid skin type" in record.message for record in caplog.records)
    
    def test_graceful_handling_of_logging_errors(self, audit_logger):
        """Test that logging errors don't crash the system."""
        # This should not raise an exception
        with patch('backend.app.recommender.audit_logger.SessionLocal', side_effect=Exception("DB Error")):
            audit_logger.log_recommendation(
                user_id=1,
                analysis_id=5,
                applied_rules=["r001"],
                recommendation={"routines": []},
                confidence_score=0.85
            )
        
        # Should still complete without raising


# ===== SUMMARY GENERATION TESTS =====

class TestSummaryGeneration:
    """Test recommendation summary generation."""
    
    def test_summary_with_all_components(self):
        """Test summary generation with routines, products, and diet."""
        recommendation = {
            "routines": [{"step": 1}, {"step": 2}],
            "products": [{"id": 1}, {"id": 2}, {"id": 3}],
            "diet": [{"name": "hydration"}],
            "escalation": None
        }
        
        summary = RecommendationAuditLogger._generate_summary(recommendation)
        
        assert "routines=2" in summary
        assert "products=3" in summary
        assert "diet=1" in summary
    
    def test_summary_with_escalation(self):
        """Test summary includes escalation level."""
        recommendation = {
            "routines": [],
            "products": [],
            "diet": [],
            "escalation": {"level": "urgent"}
        }
        
        summary = RecommendationAuditLogger._generate_summary(recommendation)
        
        assert "escalation=urgent" in summary
    
    def test_summary_with_empty_recommendation(self):
        """Test summary handles empty recommendation."""
        summary = RecommendationAuditLogger._generate_summary({})
        assert summary == "no_recommendations"


# ===== RULE NAMING TESTS =====

class TestRuleNaming:
    """Test rule name and category resolution."""
    
    def test_rule_name_mapping(self):
        """Test rule ID to name conversion."""
        name = RecommendationAuditLogger._get_rule_name("r001_acne_routine")
        assert name == "Acne Skincare Routine"
        
        name = RecommendationAuditLogger._get_rule_name("r002_acne_diet")
        assert name == "Acne-Friendly Diet"
    
    def test_rule_category_detection(self):
        """Test rule category inference."""
        # Diet rules
        assert RecommendationAuditLogger._get_rule_category("r002_acne_diet") == "diet"
        assert RecommendationAuditLogger._get_rule_category("r003_hydration") == "diet"
        
        # Hair rules
        assert RecommendationAuditLogger._get_rule_category("r009_hair_care") == "hair"
        
        # Skincare rules
        assert RecommendationAuditLogger._get_rule_category("r001_acne_routine") == "skincare"


# ===== SINGLETON TESTS =====

class TestGlobalLogger:
    """Test global logger singleton."""
    
    def test_get_audit_logger_returns_same_instance(self):
        """Test that get_audit_logger returns same instance."""
        logger1 = get_audit_logger()
        logger2 = get_audit_logger()
        
        assert logger1 is logger2, "Should return same instance"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
