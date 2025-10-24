/** @jsxImportSource react */
import React, { useState, useEffect } from "react";

interface Product {
  id: number;
  name: string;
  brand: string;
  category: string;
  price_usd?: number;
  tags: string[];
  ingredients: string[];
  dermatologically_safe: boolean;
  recommended_for: string[];
}

interface FormData {
  name: string;
  brand: string;
  category: string;
  tags: string;
  ingredients: string;
}

const API_BASE =
  (import.meta as any).env.VITE_API_URL || "http://127.0.0.1:8000";

export default function AdminRecommendations() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const [formData, setFormData] = useState<FormData>({
    name: "",
    brand: "",
    category: "cleanser",
    tags: "",
    ingredients: "",
  });

  useEffect(() => {
    fetchProducts();
  }, []);

  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => setSuccessMessage(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [successMessage]);

  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/api/v1/products`);
      if (response.ok) {
        const data = await response.json();
        setProducts(data.products || data);
        setError(null);
      } else {
        setError("Failed to fetch products");
      }
    } catch (err: any) {
      setError(`Error fetching products: ${err?.message || String(err)}`);
    } finally {
      setLoading(false);
    }
  };

  const handleAddProduct = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.name.trim() || !formData.brand.trim()) {
      setError("Name and Brand are required");
      return;
    }

    try {
      setLoading(true);

      const payload = {
        name: formData.name,
        brand: formData.brand,
        category: formData.category,
        tags: formData.tags
          .split(",")
          .map((tag: string) => tag.trim())
          .filter((tag: string) => tag),
        ingredients: formData.ingredients
          .split(",")
          .map((ing: string) => ing.trim())
          .filter((ing: string) => ing),
        dermatologically_safe: true,
        recommended_for: [],
      };

      const response = await fetch(`${API_BASE}/api/v1/products`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        setSuccessMessage("Product added successfully!");
        setFormData({
          name: "",
          brand: "",
          category: "cleanser",
          tags: "",
          ingredients: "",
        });
        setError(null);
        await fetchProducts();
      } else {
        const errorData = await response.json();
        setError(
          `Failed to add product: ${errorData.detail || "Unknown error"}`
        );
      }
    } catch (err: any) {
      setError(`Error adding product: ${err?.message || String(err)}`);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) => {
    const { name, value } = e.target;
    setFormData((prev: FormData) => ({
      ...prev,
      [name]: value,
    }));
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">Admin Panel</h1>

        {successMessage && (
          <div className="mb-6 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
            ✓ {successMessage}
          </div>
        )}

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            ✗ {error}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Add Product
            </h2>

            <form onSubmit={handleAddProduct} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Product Name *
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  placeholder="e.g., CeraVe Moisturizer"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Brand *
                </label>
                <input
                  type="text"
                  name="brand"
                  value={formData.brand}
                  onChange={handleInputChange}
                  placeholder="e.g., CeraVe"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Category
                </label>
                <select
                  name="category"
                  value={formData.category}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="cleanser">Cleanser</option>
                  <option value="moisturizer">Moisturizer</option>
                  <option value="serum">Serum</option>
                  <option value="treatment">Treatment</option>
                  <option value="sunscreen">Sunscreen</option>
                  <option value="mask">Mask</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tags (comma-separated)
                </label>
                <textarea
                  name="tags"
                  value={formData.tags}
                  onChange={handleInputChange}
                  placeholder="e.g., gentle, hydrating, hypoallergenic"
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Ingredients (comma-separated)
                </label>
                <textarea
                  name="ingredients"
                  value={formData.ingredients}
                  onChange={handleInputChange}
                  placeholder="e.g., water, glycerin, ceramides"
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-2 px-4 rounded-lg transition"
              >
                {loading ? "Adding..." : "Add Product"}
              </button>
            </form>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Products ({products.length})
            </h2>

            {loading && !products.length ? (
              <div className="text-center py-8 text-gray-500">Loading...</div>
            ) : products.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                No products found
              </div>
            ) : (
              <div className="space-y-3 max-h-[80vh] overflow-y-auto">
                {products.map((product) => (
                  <div
                    key={product.id}
                    className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition"
                  >
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h3 className="font-semibold text-gray-900">
                          {product.name}
                        </h3>
                        <p className="text-sm text-gray-600">{product.brand}</p>
                      </div>
                      {product.dermatologically_safe && (
                        <span className="inline-block bg-green-100 text-green-800 text-xs font-semibold px-2 py-1 rounded">
                          ✓ Safe
                        </span>
                      )}
                    </div>

                    <div className="text-xs text-gray-600 space-y-1">
                      <p>
                        <span className="font-medium">Category:</span>{" "}
                        {product.category}
                      </p>
                      {product.tags && product.tags.length > 0 && (
                        <p>
                          <span className="font-medium">Tags:</span>{" "}
                          {product.tags.join(", ")}
                        </p>
                      )}
                      {product.ingredients &&
                        product.ingredients.length > 0 && (
                          <p>
                            <span className="font-medium">Ingredients:</span>{" "}
                            {product.ingredients.slice(0, 3).join(", ")}
                            {product.ingredients.length > 3 && "..."}
                          </p>
                        )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
