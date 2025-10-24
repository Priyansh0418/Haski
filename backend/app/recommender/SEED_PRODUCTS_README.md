# Seed Products System

This directory contains the seed products system for populating the recommender database with initial skincare and haircare products.

## Files

### `seed_products.json`

JSON file containing 10 seed products with the following structure:

```json
{
  "name": "Product Name",
  "brand": "Brand Name",
  "category": "cleanser|moisturizer|serum|treatment|sunscreen|toner|mask|hair_shampoo|...",
  "price_usd": 899,                    // Price in cents (e.g., 899 = $8.99)
  "url": "https://...",                // Product URL
  "ingredients": [...],                // Array of ingredient names
  "tags": [...],                       // Array of tags (gentle, hydrating, etc.)
  "dermatologically_safe": true,       // Boolean
  "recommended_for": [...],            // Conditions: acne, dry_skin, sensitive, etc.
  "avoid_for": [...],                  // Conditions to avoid
  "avg_rating": 450,                   // Rating out of 500 (450 = 4.5 stars)
  "review_count": 2340,                // Number of reviews
  "source": "sephora|amazon|drugstore", // Product source
  "external_id": "unique_id"           // Unique identifier for deduplication
}
```

### `seed_products.py`

Python script that reads `seed_products.json` and inserts products into the database.

**Key Features:**

- Checks for existing products by `external_id` to avoid duplicates
- Skips products that already exist
- Provides detailed output showing what was inserted/skipped
- Includes verification mode to display all products in database
- Automatic timestamp management (created_at, updated_at)

## Usage

### 1. Running the Seed Script

From the project root directory:

```bash
python -m backend.app.recommender.seed_products
```

**Output:**

```
Loading 10 seed products...

✓ Product 'Hydrating Facial Cleanser' (CeraVe) inserted (ID: 1, external_id: cerave_cleanser_001)
✓ Product 'Salicylic Acid 2% Solution' (The Ordinary) inserted (ID: 2, external_id: ordinary_sa_001)
✓ Product 'Moisturizing Cream' (Vanicream) inserted (ID: 3, external_id: vanicream_moisturizer_001)
...

============================================================
Seeding Complete: 10 inserted, 0 skipped
Total products in database: 10
============================================================
```

### 2. Verifying Products After Seeding

Run with `--verify-after` flag to seed and then verify:

```bash
python -m backend.app.recommender.seed_products --verify-after
```

Or verify existing products without seeding:

```bash
python -m backend.app.recommender.seed_products --verify
```

**Verification Output:**

```
============================================================
Product Database Verification
============================================================
Total products: 10

ID: 1
  Name: Hydrating Facial Cleanser
  Brand: CeraVe
  Category: cleanser
  Price: $8.99
  Tags: gentle, hydrating, non-comedogenic, fragrance-free, dermatologist-recommended
  Dermatologically Safe: True
  Recommended For: dry_skin, sensitive, eczema, combination
  Rating: 4.5/5 (2340 reviews)

ID: 2
  Name: Salicylic Acid 2% Solution
  Brand: The Ordinary
  ...
```

## Seed Products Overview

The 10 seed products cover:

| #   | Product                        | Brand          | Category     | Use Case           |
| --- | ------------------------------ | -------------- | ------------ | ------------------ |
| 1   | Hydrating Facial Cleanser      | CeraVe         | cleanser     | Dry/sensitive skin |
| 2   | Salicylic Acid 2% Solution     | The Ordinary   | treatment    | Acne/blackheads    |
| 3   | Moisturizing Cream             | Vanicream      | moisturizer  | Dry/eczema         |
| 4   | Anthelios Fluid SPF 60         | La Roche-Posay | sunscreen    | All skin types     |
| 5   | Hydrating Toner                | Hada Labo      | toner        | Dehydration        |
| 6   | Niacinamide 10% + Zinc 1%      | The Ordinary   | serum        | Oily/acne          |
| 7   | Gentle Exfoliating Cleanser    | Neutrogena     | cleanser     | Acne/oily          |
| 8   | Deep Hydrating Sheet Mask      | MAC            | mask         | Hydration          |
| 9   | Retinol 0.2% in Squalane       | The Ordinary   | serum        | Anti-aging         |
| 10  | Sulfate-Free Hydrating Shampoo | SheaMoisture   | hair_shampoo | Dry/curly hair     |

## Adding More Products

To add more products to the seed data:

1. **Edit `seed_products.json`** and add a new product object with all required fields
2. **Generate a unique `external_id`** (e.g., `brand_name_lowercase_type_###`)
3. **Run the seed script** - it will automatically detect and insert the new product

Example new product entry:

```json
{
  "name": "Vitamin C Serum 15%",
  "brand": "Timeless",
  "category": "serum",
  "price_usd": 1299,
  "url": "https://www.amazon.com/Timeless-Vitamin-Serum-15-1-2oz",
  "ingredients": ["ascorbic acid", "sodium hyaluronate", "glycerin"],
  "tags": ["brightening", "antioxidant", "affordable", "vitamin-c"],
  "dermatologically_safe": true,
  "recommended_for": ["dull_skin", "fine_lines", "hyperpigmentation"],
  "avoid_for": [],
  "avg_rating": 410,
  "review_count": 1200,
  "source": "amazon",
  "external_id": "timeless_vitc_serum_001"
}
```

## Integration with Recommender

Products are referenced by the recommender system through:

1. **Rule Matching** - Rules in `rules.yml` reference products by `recommended_for` tags
2. **Budget Filtering** - User budget is matched against product `price_usd`
3. **Safety Checks** - Allergy/ingredient checks against `ingredients` array
4. **Feedback Collection** - User ratings stored for each recommended product

## Database Schema

Products are stored in the `products` table with the following fields:

```
id (PK)                          - Auto-incremented ID
name (str)                       - Product name
brand (str)                      - Product brand
category (str)                   - Product category
price_usd (int)                  - Price in cents
url (str)                        - Product URL
ingredients (JSON)               - Array of ingredients
tags (JSON)                      - Array of tags
dermatologically_safe (bool)    - Safety flag
recommended_for (JSON)          - Recommended conditions
avoid_for (JSON)                - Conditions to avoid
avg_rating (int)                - Rating out of 500
review_count (int)              - Number of reviews
source (str)                    - Source (sephora, amazon, etc.)
external_id (str, UNIQUE)       - External ID for deduplication
created_at (datetime)           - Creation timestamp
updated_at (datetime)           - Last update timestamp
```

## Error Handling

The script includes error handling for:

- Missing `seed_products.json` file
- Database connection issues
- Invalid product data
- Transaction failures (with rollback)

Errors will be displayed with ❌ prefix and details.

## Notes

- Products are identified by `external_id`, not by name, to allow updates
- Prices are stored in cents (multiply by 100 for display)
- Ratings are stored as integers out of 500 (divide by 100 for 5-star display)
- All timestamps are in UTC
- The script is idempotent - running it multiple times won't create duplicates
