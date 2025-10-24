"""
Seed Products Script

This script reads products from seed_products.json and inserts them into
the Products table if they don't already exist (based on external_id).

Usage:
    python backend/app/recommender/seed_products.py

Example:
    $ cd /path/to/haski
    $ python -m backend.app.recommender.seed_products
    Loading seed products...
    ✓ Product 'Hydrating Facial Cleanser' (CeraVe) inserted
    ✓ Product 'Salicylic Acid 2% Solution' (The Ordinary) already exists, skipping
    ...
    Completed: 8 inserted, 2 skipped
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.app.db.session import SessionLocal
from backend.app.db.base import Base
from backend.app.recommender.models import Product


def load_seed_products_json() -> List[Dict[str, Any]]:
    """Load seed products from JSON file."""
    json_path = Path(__file__).parent / "seed_products.json"
    
    if not json_path.exists():
        raise FileNotFoundError(f"seed_products.json not found at {json_path}")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    return products


def seed_products() -> None:
    """Insert seed products into database if they don't exist."""
    db = SessionLocal()
    
    try:
        # Load products from JSON
        products_data = load_seed_products_json()
        print(f"Loading {len(products_data)} seed products...\n")
        
        inserted_count = 0
        skipped_count = 0
        
        for product_data in products_data:
            # Check if product already exists by external_id
            external_id = product_data.get("external_id")
            existing = db.query(Product).filter(
                Product.external_id == external_id
            ).first()
            
            if existing:
                print(f"✓ Product '{product_data['name']}' ({product_data['brand']}) "
                      f"already exists (ID: {external_id}), skipping")
                skipped_count += 1
            else:
                # Create new product
                product = Product(
                    name=product_data["name"],
                    brand=product_data["brand"],
                    category=product_data.get("category", "other"),
                    price_usd=product_data.get("price_usd"),
                    url=product_data.get("url"),
                    ingredients=product_data.get("ingredients", []),
                    tags=product_data.get("tags", []),
                    dermatologically_safe=product_data.get("dermatologically_safe", False),
                    recommended_for=product_data.get("recommended_for", []),
                    avoid_for=product_data.get("avoid_for", []),
                    avg_rating=product_data.get("avg_rating"),
                    review_count=product_data.get("review_count", 0),
                    source=product_data.get("source", "manual"),
                    external_id=external_id,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                
                db.add(product)
                db.commit()
                
                print(f"✓ Product '{product.name}' ({product.brand}) inserted "
                      f"(ID: {product.id}, external_id: {external_id})")
                inserted_count += 1
        
        # Summary
        print(f"\n{'='*60}")
        print(f"Seeding Complete: {inserted_count} inserted, {skipped_count} skipped")
        print(f"Total products in database: {db.query(Product).count()}")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"❌ Error seeding products: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def verify_seed_products() -> None:
    """Verify that seed products were loaded correctly."""
    db = SessionLocal()
    
    try:
        products = db.query(Product).all()
        
        print(f"\n{'='*60}")
        print(f"Product Database Verification")
        print(f"{'='*60}")
        print(f"Total products: {len(products)}\n")
        
        for product in products:
            print(f"ID: {product.id}")
            print(f"  Name: {product.name}")
            print(f"  Brand: {product.brand}")
            print(f"  Category: {product.category}")
            print(f"  Price: ${product.price_usd / 100:.2f}" if product.price_usd else "  Price: N/A")
            print(f"  Tags: {', '.join(product.tags)}")
            print(f"  Dermatologically Safe: {product.dermatologically_safe}")
            print(f"  Recommended For: {', '.join(product.recommended_for)}")
            print(f"  Rating: {product.avg_rating / 100:.1f}/5 ({product.review_count} reviews)" 
                  if product.avg_rating else "  Rating: N/A")
            print()
        
    finally:
        db.close()


if __name__ == "__main__":
    """
    Main entry point for seed_products script.
    
    Loads seed products from JSON and inserts into database.
    To verify, call with --verify flag.
    """
    if len(sys.argv) > 1 and sys.argv[1] == "--verify":
        verify_seed_products()
    else:
        seed_products()
        if len(sys.argv) > 1 and sys.argv[1] == "--verify-after":
            verify_seed_products()
