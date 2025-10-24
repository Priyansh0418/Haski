# Recommender System Integration Tests

## Overview

Comprehensive integration test suite for the Haski recommender engine with three main test categories:

## Test Coverage (11 Tests - All Passing ✅)

### 1. **Rule Engine with Sample Data** (3 tests)

Tests the core recommendation engine with realistic analysis and profile data:

- `test_engine_returns_required_structure`
  - Verifies recommendation response contains required arrays: `routines`, `products`, `diet`
  - Checks data types (lists) are correct
- `test_applied_rules_returns_list`
  - Confirms `applied_rules` returns a list (can be empty)
  - Validates rule tracking works correctly
- `test_recommendation_structure_details`
  - Tests nested structure of recommendations
  - Validates routine objects have `step` or `action` fields
  - Validates product objects have `name` or `category` fields
  - Checks escalation field (None or dict)

### 2. **Product Integration** (3 tests)

Tests database persistence and product matching with analysis:

- `test_salicylic_product_in_db`
  - Creates BHA Exfoliating Cleanser product in database
  - Verifies product persistence and retrieval
  - Checks all fields saved correctly
- `test_product_tags_for_acne`
  - Queries products by tag (`salicylic_cleanser`)
  - Verifies tag-based filtering works
- `test_product_matches_analysis_conditions`
  - Matches product recommendations to analysis conditions
  - Ensures product tags align with detected skin conditions (acne, blackheads, oily_skin)

### 3. **Recommendation Record Integration** (1 test)

Tests storing generated recommendations in database:

- `test_create_recommendation_record`
  - Creates recommendation record with engine output
  - Stores recommendation content (routines, products, diet)
  - Links to analysis and user
  - Validates all fields persisted

### 4. **Feedback Integration** (3 tests)

Tests user feedback submission and aggregation:

- `test_submit_feedback`
  - Posts feedback on a recommendation
  - Validates feedback fields (helpful_rating, satisfaction, completion %)
  - Confirms feedback saved to database
- `test_aggregate_feedback_stats`
  - Creates 3 feedback records with different ratings
  - Aggregates statistics using SQL:
    - Count of feedbacks
    - Average helpful rating (4.0/5)
    - Average satisfaction (4.0/5)
    - Average routine completion (76.67%)
    - Count of positive recommendations (2/3)
- `test_feedback_request_schema`
  - Validates Pydantic schema for feedback requests
  - Tests required fields (`recommendation_id`) and optional fields
  - Validates schema validation works

### 5. **End-to-End Flow** (1 test)

Complete integration test from analysis to feedback:

- `test_analysis_to_recommendation_to_feedback`
  - Creates analysis from photo
  - Calls RuleEngine to generate recommendations
  - Stores recommendation record in database
  - Submits user feedback
  - Verifies entire pipeline works end-to-end

## Test Data

### Sample Analysis (Acne/Oily Skin)

```python
{
    "skin_type": "oily",
    "conditions_detected": ["acne", "blackheads"],
    "skin_sensitivity": "normal",
    "hair_type": "straight",
    "age": 25,
    "birth_year": 2000
}
```

### Sample Product (BHA Cleanser)

- Name: BHA Exfoliating Cleanser
- Brand: CeraVe
- Tags: `['salicylic_cleanser', 'acne-prone', 'gentle', 'exfoliating']`
- Recommended for: `['acne', 'blackheads', 'oily_skin']`
- Price: $8.99
- Rating: 4.5 stars (1200 reviews)

## Running the Tests

### Run All Tests

```bash
cd d:\Haski-main
python -m pytest backend/app/recommender/test_recommender_integration.py -v
```

### Run Specific Test Class

```bash
# Rule engine tests
python -m pytest backend/app/recommender/test_recommender_integration.py::TestRuleEngineWithSampleData -v

# Product tests
python -m pytest backend/app/recommender/test_recommender_integration.py::TestProductIntegration -v

# Feedback tests
python -m pytest backend/app/recommender/test_recommender_integration.py::TestFeedbackIntegration -v
```

### Run Single Test

```bash
python -m pytest backend/app/recommender/test_recommender_integration.py::TestFeedbackIntegration::test_aggregate_feedback_stats -v
```

## Test Results

```
====================== 11 passed in 0.68s ======================

TestRuleEngineWithSampleData::test_engine_returns_required_structure ✅
TestRuleEngineWithSampleData::test_applied_rules_returns_list ✅
TestRuleEngineWithSampleData::test_recommendation_structure_details ✅
TestProductIntegration::test_salicylic_product_in_db ✅
TestProductIntegration::test_product_tags_for_acne ✅
TestProductIntegration::test_product_matches_analysis_conditions ✅
TestRecommendationRecordIntegration::test_create_recommendation_record ✅
TestFeedbackIntegration::test_submit_feedback ✅
TestFeedbackIntegration::test_aggregate_feedback_stats ✅
TestFeedbackIntegration::test_feedback_request_schema ✅
TestEndToEndRecommendation::test_analysis_to_recommendation_to_feedback ✅
```

## Fixtures

All tests use SQLAlchemy in-memory SQLite database with automatic schema creation:

```python
@pytest.fixture
def test_db():
    """Create in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    # ...
    yield db
    db.close()
```

## Dependencies

- `pytest` - Test framework
- `sqlalchemy` - ORM and database
- `pydantic` - Schema validation
- `torch` - ML inference

## Key Test Patterns

### 1. Database Isolation

Each test gets a fresh in-memory database - no test pollution

### 2. Fixture Reuse

Common fixtures like `sample_user`, `sample_analysis`, `sample_photo` are shared across tests

### 3. End-to-End Validation

Tests verify:

- Data storage and retrieval
- Schema validation
- Relationship integrity
- SQL aggregation

### 4. Assertion Style

Clear, descriptive assertions with helpful error messages:

```python
assert isinstance(recommendation['routines'], list), \
    f"routines should be list, got {type(recommendation['routines'])}"
```

## Notes

- Tests use realistic sample data (acne/oily skin condition)
- Product recommendations verified against actual analysis conditions
- Feedback aggregation tests complex SQL queries
- All fixtures create related records (user → photo → analysis → recommendation → feedback)
- In-memory DB provides fast test execution (~0.7s for all 11 tests)

## Future Enhancements

1. Add tests for negative cases (invalid conditions, missing fields)
2. Test product filtering by budget/allergies
3. Test rule prioritization and escalation levels
4. Load testing with large feedback datasets
5. Parametrized tests for different skin conditions
6. Mock external dependencies (storage service, ML models)
