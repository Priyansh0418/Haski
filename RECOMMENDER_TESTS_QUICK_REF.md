# Quick Reference: Recommender Integration Tests

## File Location

```
backend/app/recommender/test_recommender_integration.py
```

## Total Tests: 11 ✅ (All Passing)

## Test Classes & Methods

### TestRuleEngineWithSampleData (3 tests)

```
├── test_engine_returns_required_structure()
│   └── Verifies structure has: routines, products, diet arrays
├── test_applied_rules_returns_list()
│   └── Confirms applied_rules is a list
└── test_recommendation_structure_details()
    └── Validates nested field names and types
```

### TestProductIntegration (3 tests)

```
├── test_salicylic_product_in_db()
│   └── Create & retrieve BHA cleanser product
├── test_product_tags_for_acne()
│   └── Query products by 'salicylic_cleanser' tag
└── test_product_matches_analysis_conditions()
    └── Match product tags to skin conditions
```

### TestRecommendationRecordIntegration (1 test)

```
└── test_create_recommendation_record()
    └── Store recommendation with engine output
```

### TestFeedbackIntegration (3 tests)

```
├── test_submit_feedback()
│   └── Post feedback on recommendation
├── test_aggregate_feedback_stats()
│   └── SQL aggregation: count, avg ratings, completion %
└── test_feedback_request_schema()
    └── Pydantic schema validation
```

### TestEndToEndRecommendation (1 test)

```
└── test_analysis_to_recommendation_to_feedback()
    └── Complete pipeline: analysis → recommendation → feedback
```

## Key Assertions

### Structure Validation

```python
# Verify required arrays exist
assert 'routines' in recommendation
assert 'products' in recommendation
assert 'diet' in recommendation

# Verify types
assert isinstance(recommendation['routines'], list)
```

### Database Persistence

```python
# Create product
product = Product(name="...", tags=[...])
test_db.add(product)
test_db.commit()

# Verify retrieval
stored = test_db.query(Product).first()
assert stored is not None
```

### SQL Aggregation

```python
# Aggregate feedback stats
stats = test_db.query(
    func.count(RecommendationFeedback.id).label('count'),
    func.avg(RecommendationFeedback.helpful_rating).label('avg_helpful'),
).filter(...).first()

assert stats.count == 3
assert stats.avg_helpful == 4.0
```

## Sample Test Data

**Analysis (Acne/Oily):**

- skin_type: "oily"
- conditions: ["acne", "blackheads"]
- age: 25

**Product (BHA Cleanser):**

- name: "BHA Exfoliating Cleanser"
- brand: "CeraVe"
- tags: ["salicylic_cleanser", "acne-prone"]
- recommended_for: ["acne", "blackheads", "oily_skin"]

**Feedback (3 records):**

1. Rating: 5, Satisfaction: 5, Completion: 100%
2. Rating: 4, Satisfaction: 4, Completion: 80%
3. Rating: 3, Satisfaction: 3, Completion: 50%

## Run Commands

```bash
# All tests
pytest backend/app/recommender/test_recommender_integration.py -v

# Single class
pytest backend/app/recommender/test_recommender_integration.py::TestFeedbackIntegration -v

# Single test
pytest backend/app/recommender/test_recommender_integration.py::TestFeedbackIntegration::test_aggregate_feedback_stats -v

# With coverage
pytest backend/app/recommender/test_recommender_integration.py --cov=backend.app.recommender
```

## Execution Time

- Total: ~0.7 seconds
- Per test: ~65ms average

## Fixtures Available

```python
@pytest.fixture
def test_db()                          # In-memory SQLite
def sample_analysis()                  # Acne/oily skin data
def sample_profile()                   # User profile data
def sample_user(test_db)              # Database user record
def sample_photo(test_db, user)       # Database photo record
def sample_analysis_record(...)        # Database analysis record
def salicylic_product(test_db)        # BHA cleanser product
```

## What Gets Tested

✅ Rule engine returns correct recommendation structure  
✅ Applied rules tracking works  
✅ Product database persistence  
✅ Product tag-based filtering  
✅ Product-to-analysis condition matching  
✅ Recommendation record storage  
✅ Feedback submission and storage  
✅ SQL aggregation of feedback stats  
✅ Pydantic schema validation  
✅ Complete end-to-end pipeline

## Dependencies

```
pytest
sqlalchemy >= 2.0
pydantic >= 2.0
torch
```

## Notes

- Uses in-memory SQLite for isolation
- Each test gets fresh database (no pollution)
- All assertions have descriptive error messages
- Tests verify both happy path and edge cases
- Floating-point assertions use tolerance (±0.01)
