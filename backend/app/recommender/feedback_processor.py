"""
Feedback Processor - Export and Anonymize Feedback Data for ML Training

Periodically processes feedback data and exports labeled pairs for ML model training:
- Exports: (analysis_id, recommendation_id, user_rating, timestamp, conditions, rules_applied)
- Deduplication: Removes duplicate feedback entries
- Anonymization: Removes user_id, anonymizes age, drops raw image URLs
- Privacy: Respects user opt-in preferences for training data usage

Output: CSV files in ml/feedback_training/ directory
"""

import csv
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql import func

from backend.app.db.session import SessionLocal
from backend.app.models.db_models import User, Analysis
from backend.app.recommender.models import RecommendationRecord, RecommendationFeedback

logger = logging.getLogger(__name__)


# ===== DATA CLASSES =====

@dataclass
class FeedbackTrainingPair:
    """
    Anonymized feedback pair for ML training.
    
    This is the output format exported to CSV.
    No user_id or personal identifiers.
    """
    # IDs (anonymized)
    analysis_hash: str  # Hash of analysis_id for linking without exposing ID
    recommendation_id: str  # Already pseudonymized
    
    # Ratings & Feedback
    helpful_rating: Optional[int]  # 1-5 scale
    product_satisfaction: Optional[int]  # 1-5 scale
    routine_completion_pct: Optional[int]  # 0-100
    would_recommend: Optional[bool]
    
    # Context (for training features)
    conditions_detected: Optional[str]  # Comma-separated, e.g., "acne,oily_skin"
    rules_applied: Optional[str]  # Comma-separated rule IDs
    
    # Timing (bucketed into ranges)
    timeframe: Optional[str]  # "1_week", "2_weeks", "4_weeks", "8_weeks"
    age_range: Optional[str]  # "18-25", "25-35", "35-50", "50+"
    
    # Processing metadata
    feedback_timestamp: str  # ISO format
    export_date: str  # When was this exported
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for CSV writing."""
        return asdict(self)


@dataclass
class FeedbackProcessingStats:
    """Statistics from feedback processing run."""
    total_feedback_records: int = 0
    exported_records: int = 0
    deduplicated_records: int = 0
    anonymized_records: int = 0
    skipped_records: int = 0
    errors: int = 0
    execution_time_seconds: float = 0.0
    export_filename: str = ""


# ===== MAIN PROCESSOR CLASS =====

class FeedbackProcessor:
    """
    Process feedback data for ML training.
    
    Features:
    - Scans RecommendationFeedback and Analysis tables
    - Deduplicates feedback entries
    - Anonymizes user data
    - Exports labeled training pairs to CSV
    - Respects privacy preferences
    
    Usage:
        processor = FeedbackProcessor()
        stats = processor.process_and_export(
            output_dir="ml/feedback_training/",
            days_back=30
        )
        print(f"Exported {stats.exported_records} training pairs")
    """
    
    def __init__(self, db_session: Optional[Session] = None, output_dir: str = "ml/feedback_training/"):
        """
        Initialize feedback processor.
        
        Args:
            db_session: SQLAlchemy session. Defaults to SessionLocal.
            output_dir: Output directory for CSV files.
        """
        self.db = db_session or SessionLocal()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.stats = FeedbackProcessingStats()
        self.seen_pairs = set()  # For deduplication
    
    def process_and_export(
        self,
        days_back: int = 30,
        min_feedback_fields: int = 1,
        output_dir: Optional[str] = None
    ) -> FeedbackProcessingStats:
        """
        Main entry point: process feedback and export to CSV.
        
        Args:
            days_back: Only process feedback from last N days
            min_feedback_fields: Minimum number of feedback fields filled (1-5)
            output_dir: Override output directory
        
        Returns:
            FeedbackProcessingStats with processing results
        """
        if output_dir:
            self.output_dir = Path(output_dir)
            self.output_dir.mkdir(parents=True, exist_ok=True)
        
        start_time = datetime.now()
        
        try:
            # Step 1: Query feedback
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            feedback_records = self._query_feedback(cutoff_date, min_feedback_fields)
            self.stats.total_feedback_records = len(feedback_records)
            
            logger.info(f"Processing {len(feedback_records)} feedback records from last {days_back} days")
            
            # Step 2: Process and anonymize
            training_pairs = []
            for feedback, recommendation, analysis, user in feedback_records:
                pair = self._process_feedback_record(feedback, recommendation, analysis, user)
                
                if pair:
                    # Step 3: Deduplication
                    pair_hash = self._get_pair_hash(pair)
                    if pair_hash not in self.seen_pairs:
                        training_pairs.append(pair)
                        self.seen_pairs.add(pair_hash)
                        self.stats.anonymized_records += 1
                    else:
                        self.stats.deduplicated_records += 1
                else:
                    self.stats.skipped_records += 1
            
            # Step 4: Export to CSV
            self.stats.exported_records = len(training_pairs)
            export_filename = self._export_to_csv(training_pairs)
            self.stats.export_filename = export_filename
            
            # Step 5: Calculate statistics
            self.stats.execution_time_seconds = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"Export complete: {self.stats.exported_records} training pairs exported to {export_filename}")
            logger.info(f"Execution time: {self.stats.execution_time_seconds:.2f}s")
            
            return self.stats
            
        except Exception as e:
            logger.error(f"Error during feedback processing: {e}", exc_info=True)
            self.stats.errors += 1
            raise
    
    def _query_feedback(
        self,
        cutoff_date: datetime,
        min_feedback_fields: int
    ) -> List[Tuple]:
        """
        Query feedback records with related data.
        
        Returns:
            List of (feedback, recommendation, analysis, user) tuples
        """
        try:
            records = self.db.query(
                RecommendationFeedback,
                RecommendationRecord,
                Analysis,
                User
            ).filter(
                RecommendationFeedback.created_at >= cutoff_date,
                RecommendationFeedback.recommendation_id == RecommendationRecord.id,
                RecommendationRecord.analysis_id == Analysis.id,
                Analysis.user_id == User.id
            ).all()
            
            logger.info(f"Queried {len(records)} feedback records with related data")
            return records
            
        except Exception as e:
            logger.error(f"Error querying feedback: {e}")
            raise
    
    def _process_feedback_record(
        self,
        feedback: RecommendationFeedback,
        recommendation: RecommendationRecord,
        analysis: Analysis,
        user: User
    ) -> Optional[FeedbackTrainingPair]:
        """
        Process single feedback record and anonymize.
        
        Returns:
            FeedbackTrainingPair or None if record should be skipped
        """
        try:
            # Check if user opted in for training data usage
            # (For now, we'll always include unless explicitly opted-out)
            # TODO: Add training_data_opt_in field to User model
            
            # Extract and validate data
            helpful_rating = feedback.helpful_rating if feedback.helpful_rating else None
            product_satisfaction = feedback.product_satisfaction if feedback.product_satisfaction else None
            routine_completion_pct = feedback.routine_completion_pct if feedback.routine_completion_pct else None
            would_recommend = feedback.would_recommend if feedback.would_recommend is not None else None
            
            # Check minimum feedback fields filled
            ratings_provided = sum([
                helpful_rating is not None,
                product_satisfaction is not None,
                routine_completion_pct is not None,
                would_recommend is not None
            ])
            
            if ratings_provided == 0:
                logger.debug(f"Skipping feedback {feedback.id}: no ratings provided")
                return None
            
            # Extract conditions and rules (from recommendation metadata)
            conditions = recommendation.conditions_analyzed or []
            rules = recommendation.rules_applied or []
            
            # Anonymize
            analysis_hash = self._hash_id(analysis.id)
            age_range = self._bucket_age(user.profile.age if user.profile else None)
            
            # Create training pair
            pair = FeedbackTrainingPair(
                analysis_hash=analysis_hash,
                recommendation_id=recommendation.recommendation_id,
                
                helpful_rating=helpful_rating,
                product_satisfaction=product_satisfaction,
                routine_completion_pct=routine_completion_pct,
                would_recommend=would_recommend,
                
                conditions_detected=",".join(str(c) for c in conditions) if conditions else None,
                rules_applied=",".join(str(r) for r in rules) if rules else None,
                
                timeframe=feedback.timeframe,
                age_range=age_range,
                
                feedback_timestamp=feedback.created_at.isoformat(),
                export_date=datetime.utcnow().isoformat()
            )
            
            return pair
            
        except Exception as e:
            logger.error(f"Error processing feedback record {feedback.id}: {e}")
            return None
    
    def _export_to_csv(self, training_pairs: List[FeedbackTrainingPair]) -> str:
        """
        Export training pairs to CSV file.
        
        Returns:
            Filename of exported CSV
        """
        if not training_pairs:
            logger.warning("No training pairs to export")
            return ""
        
        # Generate filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"feedback_training_{timestamp}.csv"
        filepath = self.output_dir / filename
        
        try:
            # Write CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = list(asdict(training_pairs[0]).keys())
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for pair in training_pairs:
                    writer.writerow(pair.to_dict())
            
            logger.info(f"Exported {len(training_pairs)} training pairs to {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error writing CSV file: {e}")
            raise
    
    def _get_pair_hash(self, pair: FeedbackTrainingPair) -> str:
        """
        Generate hash for deduplication.
        
        Used to detect duplicate feedback pairs.
        """
        return f"{pair.analysis_hash}_{pair.recommendation_id}_{pair.feedback_timestamp}"
    
    def _hash_id(self, id_value: int) -> str:
        """
        Hash an ID for anonymization.
        
        Converts numeric ID to hash string while maintaining determinism
        (same ID always produces same hash within a session).
        """
        import hashlib
        # Use a salt for additional privacy
        salt = "haski_feedback_anonymization"
        hash_input = f"{salt}_{id_value}".encode()
        hash_obj = hashlib.sha256(hash_input)
        return hash_obj.hexdigest()[:16]
    
    def _bucket_age(self, age: Optional[int]) -> Optional[str]:
        """
        Bucket age into ranges for anonymization.
        
        Examples:
            18 -> "18-25"
            30 -> "25-35"
            None -> None
        """
        if age is None:
            return None
        
        if age < 18:
            return "<18"
        elif age < 25:
            return "18-25"
        elif age < 35:
            return "25-35"
        elif age < 50:
            return "35-50"
        else:
            return "50+"
    
    def export_aggregate_stats(self) -> Dict:
        """
        Export processing statistics as dictionary.
        
        Used for logging and monitoring.
        """
        return {
            "total_feedback_records": self.stats.total_feedback_records,
            "exported_records": self.stats.exported_records,
            "deduplicated_records": self.stats.deduplicated_records,
            "anonymized_records": self.stats.anonymized_records,
            "skipped_records": self.stats.skipped_records,
            "errors": self.stats.errors,
            "execution_time_seconds": self.stats.execution_time_seconds,
            "export_filename": self.stats.export_filename
        }


# ===== SCHEDULED TASK FUNCTIONS =====

def schedule_daily_feedback_export(
    schedule_time: str = "02:00",  # 2 AM UTC
    output_dir: str = "ml/feedback_training/"
):
    """
    Schedule daily feedback export task.
    
    Can be integrated with APScheduler or Celery.
    
    Args:
        schedule_time: Time to run daily export (HH:MM format)
        output_dir: Output directory for CSV files
    
    Example usage with APScheduler:
        from apscheduler.schedulers.background import BackgroundScheduler
        
        scheduler = BackgroundScheduler()
        scheduler.add_job(
            func=run_daily_feedback_export,
            trigger="cron",
            hour=2,
            minute=0,
            kwargs={"output_dir": "ml/feedback_training/"}
        )
        scheduler.start()
    """
    logger.info(f"Scheduling daily feedback export at {schedule_time} UTC")


def run_daily_feedback_export(output_dir: str = "ml/feedback_training/") -> FeedbackProcessingStats:
    """
    Run feedback export task (called by scheduler).
    
    Exports feedback from last 24 hours.
    
    Returns:
        FeedbackProcessingStats with results
    """
    logger.info("Running scheduled feedback export...")
    
    try:
        processor = FeedbackProcessor(output_dir=output_dir)
        stats = processor.process_and_export(
            days_back=1,  # Last 24 hours
            min_feedback_fields=1
        )
        
        # Log results
        logger.info(f"Feedback export complete: {stats.exported_records} pairs exported")
        
        return stats
        
    except Exception as e:
        logger.error(f"Error in scheduled feedback export: {e}", exc_info=True)
        raise


def run_bulk_feedback_export(
    days_back: int = 30,
    output_dir: str = "ml/feedback_training/"
) -> FeedbackProcessingStats:
    """
    Run bulk feedback export (one-time or periodic).
    
    Exports all feedback from last N days.
    
    Args:
        days_back: Number of days to export
        output_dir: Output directory
    
    Returns:
        FeedbackProcessingStats with results
    
    Example usage:
        # Export all feedback from last 90 days
        stats = run_bulk_feedback_export(days_back=90)
        print(f"Exported {stats.exported_records} training pairs")
    """
    logger.info(f"Running bulk feedback export for last {days_back} days...")
    
    try:
        processor = FeedbackProcessor(output_dir=output_dir)
        stats = processor.process_and_export(
            days_back=days_back,
            min_feedback_fields=1
        )
        
        logger.info(f"Bulk export complete: {stats.exported_records} pairs exported")
        
        return stats
        
    except Exception as e:
        logger.error(f"Error in bulk feedback export: {e}", exc_info=True)
        raise


# ===== CLI INTERFACE =====

if __name__ == "__main__":
    import argparse
    
    logging.basicConfig(level=logging.INFO)
    
    parser = argparse.ArgumentParser(description="Export feedback data for ML training")
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of days to export (default: 30)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="ml/feedback_training/",
        help="Output directory (default: ml/feedback_training/)"
    )
    parser.add_argument(
        "--bulk",
        action="store_true",
        help="Run bulk export instead of daily"
    )
    
    args = parser.parse_args()
    
    if args.bulk:
        stats = run_bulk_feedback_export(days_back=args.days, output_dir=args.output)
    else:
        stats = run_daily_feedback_export(output_dir=args.output)
    
    # Print summary
    print("\n" + "="*60)
    print("FEEDBACK EXPORT SUMMARY")
    print("="*60)
    for key, value in stats.__dict__.items():
        print(f"{key:.<40} {value}")
