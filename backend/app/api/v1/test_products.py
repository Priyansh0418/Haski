"""
Unit tests for products API endpoint

Tests cover:
- Product listing with filtering (tag, ingredient, category, etc.)
- Pagination
- Product details retrieval
- Product creation (admin only)
- Error handling (404, 403, etc.)
- Edge cases
"""

import pytest
from datetime import datetime
from typing import Optional
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.main import app
from backend.app.db.session import get_db
from backend.app.core.security import create_access_token, get_current_user
from backend.app.models.db_models import User
from backend.app.recommender.models import Product

client = TestClient(app)


# ===== FIXTURES =====

@pytest.fixture
def db_session():
    """Get database session for tests"""
    from backend.app.db.base import Base
    from backend.app.db.session import engine
    
    Base.metadata.create_all(bind=engine)
    db = Session(bind=engine)
    yield db
    db.close()


@pytest.fixture
def admin_user(db_session: Session) -> User:
    """Create admin user for testing"""
    user = User(
        username="admin_test",
        email="admin@skinhaira.ai",
        hashed_password="hashed_password"
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def regular_user(db_session: Session) -> User:
    """Create regular user for testing"""
    user = User(
        username="user_test",
        email="user@example.com",
        hashed_password="hashed_password"
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def admin_token(admin_user: User) -> str:
    """Generate admin access token"""
    return create_access_token(data={"sub": str(admin_user.id)})


@pytest.fixture
def user_token(regular_user: User) -> str:
    """Generate regular user access token"""
    return create_access_token(data={"sub": str(regular_user.id)})


@pytest.fixture
def sample_products(db_session: Session) -> list:
    """Create sample products for testing"""
    products = [
        Product(
            name="Salicylic Acid 2%",
            brand="The Ordinary",
            category="treatment",
            price_usd=590,  # $5.90
            url="https://theordinary.deciem.com",
            ingredients=["water", "salicylic acid"],
            tags=["exfoliating", "bha", "acne-fighting"],
            dermatologically_safe=True,
            recommended_for=["acne", "blackheads"],
            avoid_for=["very_sensitive"],
            avg_rating=430,  # 4.3/5
            review_count=5890,
            source="the_ordinary",
            external_id="ordinary_sa_001",
            created_at=datetime.utcnow()
        ),
        Product(
            name="Niacinamide 10%",
            brand="The Ordinary",
            category="treatment",
            price_usd=690,  # $6.90
            url="https://theordinary.deciem.com",
            ingredients=["water", "niacinamide"],
            tags=["anti-inflammatory", "pore-minimizing"],
            dermatologically_safe=True,
            recommended_for=["oily", "combination"],
            avoid_for=[],
            avg_rating=450,  # 4.5/5
            review_count=8120,
            source="the_ordinary",
            external_id="ordinary_nia_001",
            created_at=datetime.utcnow()
        ),
        Product(
            name="Hydrating Cleanser",
            brand="CeraVe",
            category="cleanser",
            price_usd=890,  # $8.90
            url="https://cerave.com",
            ingredients=["water", "cetyl alcohol", "ceramides"],
            tags=["cleanser", "hydrating", "gentle"],
            dermatologically_safe=True,
            recommended_for=["dry", "sensitive"],
            avoid_for=[],
            avg_rating=470,  # 4.7/5
            review_count=12450,
            source="cerave",
            external_id="cerave_cleanser_001",
            created_at=datetime.utcnow()
        ),
        Product(
            name="Moisturizing Cream",
            brand="CeraVe",
            category="moisturizer",
            price_usd=1590,  # $15.90
            url="https://cerave.com",
            ingredients=["water", "ceramides", "hyaluronic acid"],
            tags=["moisturizer", "hydrating", "safe-for-sensitive"],
            dermatologically_safe=True,
            recommended_for=["dry", "sensitive"],
            avoid_for=[],
            avg_rating=480,  # 4.8/5
            review_count=15680,
            source="cerave",
            external_id="cerave_moisturizer_001",
            created_at=datetime.utcnow()
        ),
        Product(
            name="Glycolic Acid Toner",
            brand="The Ordinary",
            category="treatment",
            price_usd=1190,  # $11.90
            url="https://theordinary.deciem.com",
            ingredients=["water", "glycolic acid"],
            tags=["exfoliating", "aha", "anti-aging"],
            dermatologically_safe=False,
            recommended_for=["mature", "dull"],
            avoid_for=["pregnant", "very_sensitive"],
            avg_rating=420,  # 4.2/5
            review_count=4560,
            source="the_ordinary",
            external_id="ordinary_aha_001",
            created_at=datetime.utcnow()
        ),
    ]
    
    for product in products:
        db_session.add(product)
    
    db_session.commit()
    return products


# ===== TESTS: LIST PRODUCTS =====

class TestProductListing:
    """Tests for GET /products endpoint"""
    
    def test_list_products_empty(self, db_session: Session):
        """Test listing products when database is empty"""
        response = client.get("/api/v1/products/products")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["page_size"] == 20
        assert data["total_pages"] == 0
        assert data["products"] == []
    
    def test_list_products_with_results(self, db_session: Session, sample_products: list):
        """Test listing products with results"""
        response = client.get("/api/v1/products/products")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["products"]) == 5
        assert data["page"] == 1
        assert data["total_pages"] == 1
    
    def test_list_products_pagination_first_page(self, db_session: Session, sample_products: list):
        """Test pagination on first page"""
        response = client.get("/api/v1/products/products?page=1&page_size=2")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["products"]) == 2
        assert data["page"] == 1
        assert data["page_size"] == 2
        assert data["total_pages"] == 3
    
    def test_list_products_pagination_second_page(self, db_session: Session, sample_products: list):
        """Test pagination on second page"""
        response = client.get("/api/v1/products/products?page=2&page_size=2")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["products"]) == 2
        assert data["page"] == 2
    
    def test_list_products_pagination_last_page(self, db_session: Session, sample_products: list):
        """Test pagination on last page (fewer items)"""
        response = client.get("/api/v1/products/products?page=3&page_size=2")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["products"]) == 1  # Only 1 item on last page
        assert data["page"] == 3
    
    def test_list_products_filter_by_tag(self, db_session: Session, sample_products: list):
        """Test filtering by tag"""
        response = client.get("/api/v1/products/products?tag=cleanser")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["products"][0]["name"] == "Hydrating Cleanser"
    
    def test_list_products_filter_by_tag_case_insensitive(self, db_session: Session, sample_products: list):
        """Test that tag filter is case-insensitive"""
        response = client.get("/api/v1/products/products?tag=CLEANSER")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
    
    def test_list_products_filter_by_ingredient(self, db_session: Session, sample_products: list):
        """Test filtering by ingredient"""
        response = client.get("/api/v1/products/products?ingredient=salicylic%20acid")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["products"][0]["name"] == "Salicylic Acid 2%"
    
    def test_list_products_filter_by_category(self, db_session: Session, sample_products: list):
        """Test filtering by category"""
        response = client.get("/api/v1/products/products?category=cleanser")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["products"][0]["category"] == "cleanser"
    
    def test_list_products_filter_by_min_rating(self, db_session: Session, sample_products: list):
        """Test filtering by minimum rating"""
        response = client.get("/api/v1/products/products?min_rating=4.5")
        
        assert response.status_code == 200
        data = response.json()
        # Products with rating >= 4.5: Niacinamide (4.5), Hydrating Cleanser (4.7), Moisturizing Cream (4.8)
        assert data["total"] == 3
    
    def test_list_products_filter_by_max_price(self, db_session: Session, sample_products: list):
        """Test filtering by maximum price"""
        response = client.get("/api/v1/products/products?max_price=10")
        
        assert response.status_code == 200
        data = response.json()
        # Products with price <= $10: SA2% (5.90), Niacinamide (6.90), Hydrating Cleanser (8.90)
        assert data["total"] == 3
    
    def test_list_products_filter_by_dermatologically_safe(self, db_session: Session, sample_products: list):
        """Test filtering by dermatological safety"""
        response = client.get("/api/v1/products/products?dermatologically_safe=false")
        
        assert response.status_code == 200
        data = response.json()
        # Only Glycolic Acid Toner is not safe
        assert data["total"] == 1
        assert data["products"][0]["name"] == "Glycolic Acid Toner"
    
    def test_list_products_filter_combined(self, db_session: Session, sample_products: list):
        """Test combined filters (tag + category)"""
        response = client.get("/api/v1/products/products?tag=exfoliating&category=treatment")
        
        assert response.status_code == 200
        data = response.json()
        # Salicylic Acid 2% and Glycolic Acid Toner are exfoliating treatments
        assert data["total"] == 2
    
    def test_list_products_search_by_brand(self, db_session: Session, sample_products: list):
        """Test search by brand"""
        response = client.get("/api/v1/products/products?search=cerave")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert all("CeraVe" in p["brand"] for p in data["products"])
    
    def test_list_products_search_by_name(self, db_session: Session, sample_products: list):
        """Test search by name"""
        response = client.get("/api/v1/products/products?search=cleanser")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert "Cleanser" in data["products"][0]["name"]
    
    def test_list_products_sort_by_rating_desc(self, db_session: Session, sample_products: list):
        """Test sorting by rating (descending)"""
        response = client.get("/api/v1/products/products?sort_by=rating&sort_order=desc")
        
        assert response.status_code == 200
        data = response.json()
        # Should be sorted from highest to lowest rating
        ratings = [p["avg_rating"] for p in data["products"]]
        assert ratings == sorted(ratings, reverse=True)
    
    def test_list_products_sort_by_price_asc(self, db_session: Session, sample_products: list):
        """Test sorting by price (ascending)"""
        response = client.get("/api/v1/products/products?sort_by=price&sort_order=asc")
        
        assert response.status_code == 200
        data = response.json()
        # Should be sorted from lowest to highest price
        prices = [p["price_usd"] for p in data["products"]]
        assert prices == sorted(prices)
    
    def test_list_products_sort_by_name(self, db_session: Session, sample_products: list):
        """Test sorting by name"""
        response = client.get("/api/v1/products/products?sort_by=name&sort_order=asc")
        
        assert response.status_code == 200
        data = response.json()
        names = [p["name"] for p in data["products"]]
        assert names == sorted(names)
    
    def test_list_products_invalid_page(self, db_session: Session, sample_products: list):
        """Test invalid page number"""
        response = client.get("/api/v1/products/products?page=0")
        
        assert response.status_code == 422  # Validation error
    
    def test_list_products_invalid_page_size(self, db_session: Session, sample_products: list):
        """Test page size exceeds limit"""
        response = client.get("/api/v1/products/products?page_size=200")
        
        assert response.status_code == 422  # Validation error


# ===== TESTS: GET PRODUCT DETAILS =====

class TestProductDetails:
    """Tests for GET /products/{id} endpoint"""
    
    def test_get_product_found(self, db_session: Session, sample_products: list):
        """Test retrieving existing product"""
        product_id = sample_products[0].id
        response = client.get(f"/api/v1/products/products/{product_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == product_id
        assert data["name"] == "Salicylic Acid 2%"
        assert data["brand"] == "The Ordinary"
        assert data["price_usd"] == 5.90
        assert "salicylic acid" in data["ingredients"]
        assert "exfoliating" in data["tags"]
    
    def test_get_product_not_found(self, db_session: Session):
        """Test retrieving non-existent product"""
        response = client.get("/api/v1/products/products/99999")
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_get_product_all_fields(self, db_session: Session, sample_products: list):
        """Test that all product fields are returned"""
        product_id = sample_products[0].id
        response = client.get(f"/api/v1/products/products/{product_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check all expected fields
        assert "id" in data
        assert "name" in data
        assert "brand" in data
        assert "category" in data
        assert "price_usd" in data
        assert "url" in data
        assert "ingredients" in data
        assert "tags" in data
        assert "dermatologically_safe" in data
        assert "recommended_for" in data
        assert "avoid_for" in data
        assert "avg_rating" in data
        assert "review_count" in data
        assert "source" in data
        assert "external_id" in data
        assert "created_at" in data


# ===== TESTS: CREATE PRODUCT =====

class TestProductCreation:
    """Tests for POST /products endpoint"""
    
    def test_create_product_admin_success(self, db_session: Session, admin_token: str):
        """Test successful product creation by admin"""
        product_data = {
            "name": "New Product",
            "brand": "Test Brand",
            "category": "cleanser",
            "price_usd": 19.99,
            "url": "https://example.com",
            "ingredients": ["ingredient1", "ingredient2"],
            "tags": ["tag1", "tag2"],
            "dermatologically_safe": True,
            "recommended_for": ["oily"],
            "avoid_for": ["sensitive"],
            "avg_rating": 4.5,
            "review_count": 100,
            "source": "test",
            "external_id": "test_001"
        }
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.post(
            "/api/v1/products/products",
            json=product_data,
            headers=headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Product"
        assert data["brand"] == "Test Brand"
        assert data["price_usd"] == 19.99
        assert data["avg_rating"] == 4.5
        assert "id" in data
    
    def test_create_product_non_admin_forbidden(self, db_session: Session, user_token: str):
        """Test that non-admin cannot create product"""
        product_data = {
            "name": "New Product",
            "brand": "Test Brand",
            "category": "cleanser"
        }
        
        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.post(
            "/api/v1/products/products",
            json=product_data,
            headers=headers
        )
        
        assert response.status_code == 403
    
    def test_create_product_no_auth(self, db_session: Session):
        """Test that unauthenticated request fails"""
        product_data = {
            "name": "New Product",
            "brand": "Test Brand",
            "category": "cleanser"
        }
        
        response = client.post(
            "/api/v1/products/products",
            json=product_data
        )
        
        assert response.status_code == 403
    
    def test_create_product_duplicate_external_id(self, db_session: Session, admin_token: str, sample_products: list):
        """Test creating product with duplicate external_id"""
        product_data = {
            "name": "Duplicate Product",
            "brand": "Test Brand",
            "category": "cleanser",
            "external_id": "ordinary_sa_001"  # Already exists
        }
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.post(
            "/api/v1/products/products",
            json=product_data,
            headers=headers
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "already exists" in data["detail"].lower()
    
    def test_create_product_minimal_fields(self, db_session: Session, admin_token: str):
        """Test creating product with minimal required fields"""
        product_data = {
            "name": "Minimal Product",
            "brand": "Test Brand",
            "category": "cleanser",
            "dermatologically_safe": True
        }
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.post(
            "/api/v1/products/products",
            json=product_data,
            headers=headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Minimal Product"
        assert data["brand"] == "Test Brand"
        assert data["dermatologically_safe"] is True
        assert data["review_count"] == 0
        assert data["ingredients"] == []
    
    def test_create_product_missing_required_field(self, db_session: Session, admin_token: str):
        """Test creating product with missing required field"""
        product_data = {
            "brand": "Test Brand",  # Missing name
            "category": "cleanser"
        }
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.post(
            "/api/v1/products/products",
            json=product_data,
            headers=headers
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_create_product_tags_lowercase(self, db_session: Session, admin_token: str):
        """Test that tags are converted to lowercase"""
        product_data = {
            "name": "Test Product",
            "brand": "Test Brand",
            "category": "cleanser",
            "tags": ["TAG1", "Tag2", "tag3"]
        }
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.post(
            "/api/v1/products/products",
            json=product_data,
            headers=headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert all(tag.islower() or tag.isdigit() for tag in data["tags"])


# ===== TESTS: UTILITY ENDPOINTS =====

class TestProductUtilities:
    """Tests for utility endpoints"""
    
    def test_list_available_tags(self, db_session: Session, sample_products: list):
        """Test listing available tags"""
        response = client.get("/api/v1/products/products/search/tags")
        
        assert response.status_code == 200
        data = response.json()
        assert "tags" in data
        assert "total" in data
        assert len(data["tags"]) > 0
        assert data["total"] == len(data["tags"])
        # Verify specific tags exist
        assert "cleanser" in data["tags"]
        assert "exfoliating" in data["tags"]
    
    def test_list_available_ingredients(self, db_session: Session, sample_products: list):
        """Test listing available ingredients"""
        response = client.get("/api/v1/products/products/search/ingredients")
        
        assert response.status_code == 200
        data = response.json()
        assert "ingredients" in data
        assert "total" in data
        assert len(data["ingredients"]) > 0
        assert data["total"] == len(data["ingredients"])
        # Verify specific ingredients exist
        assert "water" in data["ingredients"]
        assert "salicylic acid" in data["ingredients"]
    
    def test_get_category_stats(self, db_session: Session, sample_products: list):
        """Test getting category statistics"""
        response = client.get("/api/v1/products/stats/categories")
        
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert "total" in data
        assert data["total"] == 5
        # Check specific categories
        assert "treatment" in data["categories"]
        assert "cleanser" in data["categories"]
        assert "moisturizer" in data["categories"]
        assert data["categories"]["treatment"] == 3


# ===== TESTS: EDGE CASES =====

class TestEdgeCases:
    """Tests for edge cases and error scenarios"""
    
    def test_product_response_format_price_conversion(self, db_session: Session, sample_products: list):
        """Test that price is correctly converted from cents to dollars"""
        product = sample_products[0]
        response = client.get(f"/api/v1/products/products/{product.id}")
        
        assert response.status_code == 200
        data = response.json()
        # Price should be in dollars, not cents
        assert data["price_usd"] == 5.90
        assert isinstance(data["price_usd"], float)
    
    def test_product_response_format_rating_conversion(self, db_session: Session, sample_products: list):
        """Test that rating is correctly converted"""
        product = sample_products[0]
        response = client.get(f"/api/v1/products/products/{product.id}")
        
        assert response.status_code == 200
        data = response.json()
        # Rating should be out of 5, not 500
        assert data["avg_rating"] == 4.3
        assert isinstance(data["avg_rating"], float)
    
    def test_filter_with_special_characters(self, db_session: Session, sample_products: list):
        """Test filtering with special characters in search"""
        response = client.get("/api/v1/products/products?search=The%20Ordinary")
        
        assert response.status_code == 200
        data = response.json()
        assert all("The Ordinary" in p["brand"] for p in data["products"])
    
    def test_multiple_filters_no_results(self, db_session: Session, sample_products: list):
        """Test multiple filters that result in no products"""
        response = client.get(
            "/api/v1/products/products?tag=exfoliating&category=moisturizer"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["products"] == []
    
    def test_pagination_beyond_total(self, db_session: Session, sample_products: list):
        """Test requesting page beyond available pages"""
        response = client.get("/api/v1/products/products?page=100&page_size=10")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["products"]) == 0  # Empty page


# ===== INTEGRATION TESTS =====

class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_complete_product_workflow(self, db_session: Session, admin_token: str):
        """Test complete workflow: create, list, and get product"""
        # Create product
        product_data = {
            "name": "Test Integration Product",
            "brand": "Integration Tests",
            "category": "treatment",
            "price_usd": 12.99,
            "tags": ["test", "integration"],
            "external_id": "integration_001"
        }
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        create_response = client.post(
            "/api/v1/products/products",
            json=product_data,
            headers=headers
        )
        assert create_response.status_code == 201
        created_product = create_response.json()
        product_id = created_product["id"]
        
        # List products and find created product
        list_response = client.get("/api/v1/products/products")
        assert list_response.status_code == 200
        list_data = list_response.json()
        found = any(p["id"] == product_id for p in list_data["products"])
        assert found
        
        # Get product details
        get_response = client.get(f"/api/v1/products/products/{product_id}")
        assert get_response.status_code == 200
        get_data = get_response.json()
        assert get_data["id"] == product_id
        assert get_data["name"] == "Test Integration Product"
    
    def test_filter_then_detail_workflow(self, db_session: Session, sample_products: list):
        """Test filtering products then getting details"""
        # Filter by brand
        filter_response = client.get("/api/v1/products/products?search=cerave")
        assert filter_response.status_code == 200
        filter_data = filter_response.json()
        assert filter_data["total"] == 2
        
        # Get details for first result
        first_product = filter_data["products"][0]
        detail_response = client.get(f"/api/v1/products/products/{first_product['id']}")
        assert detail_response.status_code == 200
        detail_data = detail_response.json()
        assert detail_data["brand"] == "CeraVe"
