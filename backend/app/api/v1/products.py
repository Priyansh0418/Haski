"""
FastAPI Router for Product Management

Handles:
- GET /products - List products with filtering and pagination
  * Filter by tag, ingredient, category, etc.
  * Pagination support (page, page_size)
  * Sorting by rating, price, newest
  
- GET /products/{id} - Get single product details

- POST /products (admin only) - Create new product
  * Requires admin role
  * Add new products for recommendations
  * Used for database maintenance and seeding
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from ...db.session import get_db
from ...core.security import get_current_user
from ...models.db_models import User
from ...recommender.models import Product
from ...recommender.schemas import ProductCreate

logger = logging.getLogger(__name__)
router = APIRouter()


# ===== SCHEMAS =====

class ProductResponse(BaseModel):
    """Single product response"""
    id: int
    name: str
    brand: str
    category: str
    price_usd: Optional[float] = None
    url: Optional[str] = None
    ingredients: List[str] = []
    tags: List[str] = []
    dermatologically_safe: bool
    recommended_for: List[str] = []
    avoid_for: List[str] = []
    avg_rating: Optional[float] = None
    review_count: int
    source: Optional[str] = None
    external_id: Optional[str] = None
    created_at: Optional[str] = None
    
    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """Paginated product list response"""
    total: int
    page: int
    page_size: int
    total_pages: int
    products: List[ProductResponse]


class ProductCreateRequest(BaseModel):
    """Request to create a new product"""
    name: str
    brand: str
    category: str
    price_usd: Optional[float] = None
    url: Optional[str] = None
    ingredients: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    dermatologically_safe: bool = True
    recommended_for: Optional[List[str]] = None
    avoid_for: Optional[List[str]] = None
    avg_rating: Optional[float] = None
    review_count: int = 0
    source: Optional[str] = None
    external_id: Optional[str] = None
    
    class Config:
        example = {
            "name": "Salicylic Acid 2%",
            "brand": "The Ordinary",
            "category": "treatment",
            "price_usd": 5.90,
            "url": "https://theordinary.deciem.com",
            "ingredients": ["water", "salicylic acid"],
            "tags": ["exfoliating", "BHA", "acne-fighting"],
            "recommended_for": ["acne", "blackheads"],
            "avoid_for": ["very_sensitive"],
            "avg_rating": 4.3,
            "review_count": 5890,
            "source": "the_ordinary",
            "external_id": "ordinary_sa_001"
        }


# ===== HELPER FUNCTIONS =====

def _is_admin(user: User) -> bool:
    """
    Check if user is admin.
    
    For now, checking email domain for admin.
    In production, use proper admin role field.
    
    Args:
        user: User object
    
    Returns:
        True if user is admin, False otherwise
    """
    # TODO: Add is_admin field to User model
    # For now, check email domain or hardcode admin emails
    if user and user.email:
        admin_emails = [
            "admin@skinhaira.ai",
            "admin@example.com",
            "priyansh0418@gmail.com"  # Default admin for testing
        ]
        return user.email in admin_emails
    return False


def _validate_is_admin(user: User) -> None:
    """
    Validate that user is admin.
    
    Args:
        user: User object
    
    Raises:
        HTTPException: 403 if not admin
    """
    if not _is_admin(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )


def _build_product_response(product: Product) -> ProductResponse:
    """
    Build product response from database object.
    
    Args:
        product: Product database object
    
    Returns:
        ProductResponse dict
    """
    return ProductResponse(
        id=product.id,
        name=product.name,
        brand=product.brand,
        category=product.category,
        price_usd=product.price_usd / 100 if product.price_usd else None,
        url=product.url,
        ingredients=product.ingredients or [],
        tags=product.tags or [],
        dermatologically_safe=product.dermatologically_safe,
        recommended_for=product.recommended_for or [],
        avoid_for=product.avoid_for or [],
        avg_rating=product.avg_rating / 100 if product.avg_rating else None,
        review_count=product.review_count or 0,
        source=product.source,
        external_id=product.external_id,
        created_at=product.created_at.isoformat() if product.created_at else None
    )


def _apply_product_filters(
    query,
    tag: Optional[str] = None,
    ingredient: Optional[str] = None,
    category: Optional[str] = None,
    min_rating: Optional[float] = None,
    max_price: Optional[float] = None,
    dermatologically_safe: Optional[bool] = None,
    search: Optional[str] = None
) -> Any:
    """
    Apply filters to product query.
    
    Args:
        query: SQLAlchemy query object
        tag: Filter by tag (case-insensitive contains)
        ingredient: Filter by ingredient (case-insensitive contains)
        category: Filter by category (exact match)
        min_rating: Filter by minimum rating (out of 5.0)
        max_price: Filter by maximum price USD
        dermatologically_safe: Filter by safety
        search: Search by name/brand (contains)
    
    Returns:
        Filtered query
    """
    if tag:
        # Filter products that have the tag in their tags array
        # For SQLite compatibility, use LIKE on JSON text
        tag_lower = tag.lower()
        # Search for the tag as a quoted JSON string within the JSON array
        query = query.filter(Product.tags.astext.ilike(f'%{tag_lower}%'))
    
    if ingredient:
        # Filter products that have the ingredient
        # For SQLite compatibility, use LIKE on JSON text
        ingredient_lower = ingredient.lower()
        query = query.filter(Product.ingredients.astext.ilike(f'%{ingredient_lower}%'))
    
    if category:
        query = query.filter(Product.category == category.lower())
    
    if min_rating is not None:
        # Rating stored as integer out of 500 (e.g., 450 = 4.5)
        min_rating_int = int(min_rating * 100)
        query = query.filter(Product.avg_rating >= min_rating_int)
    
    if max_price is not None:
        # Price stored in cents
        max_price_cents = int(max_price * 100)
        query = query.filter(Product.price_usd <= max_price_cents)
    
    if dermatologically_safe is not None:
        query = query.filter(Product.dermatologically_safe == dermatologically_safe)
    
    if search:
        # Search in name or brand
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Product.name.ilike(search_term),
                Product.brand.ilike(search_term)
            )
        )
    
    return query


# ===== ENDPOINTS =====

@router.get("", response_model=ProductListResponse)
def list_products(
    tag: Optional[str] = Query(None, description="Filter by tag (e.g., 'cleanser', 'acne-fighting')"),
    ingredient: Optional[str] = Query(None, description="Filter by ingredient (e.g., 'salicylic acid')"),
    category: Optional[str] = Query(None, description="Filter by category (e.g., 'cleanser', 'moisturizer')"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Minimum rating (0-5)"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price in USD"),
    dermatologically_safe: Optional[bool] = Query(None, description="Filter by dermatological safety"),
    search: Optional[str] = Query(None, description="Search by name or brand"),
    sort_by: str = Query("rating", regex="^(rating|price|newest|name)$", description="Sort by: rating, price, newest, name"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order: asc or desc"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page (1-100)"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    List products with filtering and pagination.
    
    Supports filtering by:
    - tag: Product tags (e.g., 'cleanser', 'exfoliating', 'acne-fighting')
    - ingredient: Ingredient names (case-insensitive)
    - category: Product category (cleanser, moisturizer, treatment, etc.)
    - min_rating: Minimum rating (0-5 scale)
    - max_price: Maximum price in USD
    - dermatologically_safe: Safety certification
    - search: Full-text search by name/brand
    
    Supports sorting by:
    - rating: Average product rating (descending by default)
    - price: Product price (ascending by default)
    - newest: Recently added products
    - name: Product name (A-Z)
    
    Supports pagination:
    - page: Page number (1-indexed)
    - page_size: Items per page (1-100)
    
    Args:
        tag: Filter by product tag
        ingredient: Filter by ingredient
        category: Filter by category
        min_rating: Minimum rating filter
        max_price: Maximum price filter
        dermatologically_safe: Safety filter
        search: Text search
        sort_by: Sort field
        sort_order: Sort direction
        page: Page number
        page_size: Items per page
        db: Database session
    
    Returns:
        {
            "total": 42,
            "page": 1,
            "page_size": 20,
            "total_pages": 3,
            "products": [
                {
                    "id": 1,
                    "name": "Salicylic Acid 2%",
                    "brand": "The Ordinary",
                    "category": "treatment",
                    "price_usd": 5.90,
                    "tags": ["exfoliating", "BHA", "acne-fighting"],
                    "avg_rating": 4.3,
                    "review_count": 5890,
                    ...
                }
            ]
        }
    
    Examples:
        GET /products?tag=cleanser&page_size=10
        GET /products?ingredient=salicylic%20acid&min_rating=4&sort_by=rating
        GET /products?category=moisturizer&max_price=30&sort_by=price&sort_order=asc
        GET /products?search=ordinary&sort_by=newest
    """
    try:
        # Start with base query
        query = db.query(Product)
        
        # Apply filters
        query = _apply_product_filters(
            query,
            tag=tag,
            ingredient=ingredient,
            category=category,
            min_rating=min_rating,
            max_price=max_price,
            dermatologically_safe=dermatologically_safe,
            search=search
        )
        
        # Get total count before pagination
        total = query.count()
        
        # Apply sorting
        if sort_by == "rating":
            query = query.order_by(
                Product.avg_rating.desc() if sort_order == "desc" else Product.avg_rating.asc()
            )
        elif sort_by == "price":
            query = query.order_by(
                Product.price_usd.asc() if sort_order == "asc" else Product.price_usd.desc()
            )
        elif sort_by == "newest":
            query = query.order_by(
                Product.created_at.desc() if sort_order == "desc" else Product.created_at.asc()
            )
        elif sort_by == "name":
            query = query.order_by(
                Product.name.asc() if sort_order == "asc" else Product.name.desc()
            )
        
        # Apply pagination
        offset = (page - 1) * page_size
        products = query.offset(offset).limit(page_size).all()
        
        # Calculate total pages
        total_pages = (total + page_size - 1) // page_size
        
        # Build response
        product_responses = [_build_product_response(p) for p in products]
        
        logger.info(
            f"Listed products: total={total}, page={page}, page_size={page_size}, "
            f"filters: tag={tag}, ingredient={ingredient}, category={category}"
        )
        
        return ProductListResponse(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            products=product_responses
        )
    
    except Exception as e:
        logger.error(f"Error listing products: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list products"
        )


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int = Path(..., description="Product ID"),
    db: Session = Depends(get_db)
) -> ProductResponse:
    """
    Get single product details by ID.
    
    Args:
        product_id: ID of product to retrieve
        db: Database session
    
    Returns:
        ProductResponse with complete product details
    
    Raises:
        HTTPException: 404 if product not found
    """
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {product_id} not found"
            )
        
        logger.info(f"Retrieved product: id={product_id}, name={product.name}")
        
        return _build_product_response(product)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving product {product_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve product"
        )


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    request: ProductCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ProductResponse:
    """
    Create a new product (admin only).
    
    This endpoint allows admins to add new products to the database
    for recommendations. Used for database maintenance and seeding.
    
    Requires admin privileges. Admin status checked via email domain or role.
    
    Args:
        request: ProductCreateRequest with product details
        db: Database session
        current_user: Current user (must be admin)
    
    Returns:
        Created ProductResponse
    
    Raises:
        HTTPException: 403 if not admin
        HTTPException: 400 if duplicate external_id
        HTTPException: 422 if validation fails
    """
    try:
        # Validate admin access
        _validate_is_admin(current_user)
        
        # Check for duplicate external_id
        if request.external_id:
            existing = db.query(Product).filter(
                Product.external_id == request.external_id
            ).first()
            
            if existing:
                logger.warning(
                    f"Duplicate product external_id: {request.external_id}, "
                    f"existing: id={existing.id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product with external_id '{request.external_id}' already exists"
                )
        
        # Convert price to cents
        price_cents = None
        if request.price_usd is not None:
            price_cents = int(request.price_usd * 100)
        
        # Convert rating to integer (out of 500)
        avg_rating = None
        if request.avg_rating is not None:
            avg_rating = int(request.avg_rating * 100)
        
        # Create product
        product = Product(
            name=request.name,
            brand=request.brand,
            category=request.category.lower(),
            price_usd=price_cents,
            url=request.url,
            ingredients=request.ingredients,
            tags=[t.lower() for t in (request.tags or [])],
            dermatologically_safe=request.dermatologically_safe,
            recommended_for=request.recommended_for,
            avoid_for=request.avoid_for,
            avg_rating=avg_rating,
            review_count=request.review_count,
            source=request.source,
            external_id=request.external_id,
            created_at=datetime.utcnow()
        )
        
        db.add(product)
        db.commit()
        db.refresh(product)
        
        logger.info(
            f"Created product: id={product.id}, name={product.name}, "
            f"brand={product.brand}, admin_user={current_user.email}"
        )
        
        return _build_product_response(product)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating product: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create product"
        )


# ===== UTILITY ENDPOINTS =====

@router.get("/search/tags")
def list_available_tags(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get list of all available product tags (for autocomplete).
    
    Returns all unique tags used in the products database,
    useful for building filter UIs.
    
    Args:
        db: Database session
    
    Returns:
        {
            "tags": ["acne-fighting", "BHA", "cleanser", ...],
            "total": 24
        }
    """
    try:
        # Query all products and extract unique tags
        products = db.query(Product.tags).all()
        
        all_tags = set()
        for product_tags in products:
            if product_tags[0]:
                all_tags.update(product_tags[0])
        
        sorted_tags = sorted(list(all_tags))
        
        logger.info(f"Retrieved {len(sorted_tags)} unique tags")
        
        return {
            "tags": sorted_tags,
            "total": len(sorted_tags)
        }
    
    except Exception as e:
        logger.error(f"Error listing tags: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list tags"
        )


@router.get("/search/ingredients")
def list_available_ingredients(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get list of all available ingredients (for autocomplete).
    
    Returns all unique ingredients used in the products database.
    
    Args:
        db: Database session
    
    Returns:
        {
            "ingredients": ["salicylic acid", "glycerin", "niacinamide", ...],
            "total": 156
        }
    """
    try:
        # Query all products and extract unique ingredients
        products = db.query(Product.ingredients).all()
        
        all_ingredients = set()
        for product_ingredients in products:
            if product_ingredients[0]:
                all_ingredients.update(product_ingredients[0])
        
        sorted_ingredients = sorted(list(all_ingredients))
        
        logger.info(f"Retrieved {len(sorted_ingredients)} unique ingredients")
        
        return {
            "ingredients": sorted_ingredients,
            "total": len(sorted_ingredients)
        }
    
    except Exception as e:
        logger.error(f"Error listing ingredients: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list ingredients"
        )


@router.get("/stats/categories")
def get_category_stats(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get product count by category (for analytics).
    
    Returns number of products in each category.
    
    Args:
        db: Database session
    
    Returns:
        {
            "categories": {
                "cleanser": 12,
                "moisturizer": 8,
                "treatment": 15,
                ...
            },
            "total": 42
        }
    """
    try:
        # Query products grouped by category
        results = db.query(
            Product.category,
            func.count(Product.id).label("count")
        ).group_by(Product.category).all()
        
        categories = {cat: count for cat, count in results}
        total = sum(categories.values())
        
        logger.info(f"Retrieved category stats: {len(categories)} categories, {total} products")
        
        return {
            "categories": categories,
            "total": total
        }
    
    except Exception as e:
        logger.error(f"Error getting category stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get category stats"
        )
