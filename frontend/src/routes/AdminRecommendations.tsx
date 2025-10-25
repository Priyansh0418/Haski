import React, { useState, useEffect } from "react";

interface Product {
  id: number;
  name: string;
  brand: string;
  category: string;
  tags: string[];
  ingredients: string[];
  dermatologically_safe: boolean;
}

const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export default function AdminRecommendations() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    name: "",
    brand: "",
    category: "cleanser",
    tags: "",
    ingredients: "",
  });

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/api/v1/products`);
      if (response.ok) {
        const data = await response.json();
        setProducts(data.products || data);
      } else {
        setError("Failed to fetch products");
      }
    } catch (err: any) {
      setError(err?.message || "Error fetching products");
    } finally {
      setLoading(false);
    }
  };

  const handleAddProduct = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name.trim() || !formData.brand.trim()) {
      setError("Name and Brand required");
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
          .map((t: string) => t.trim())
          .filter(Boolean),
        ingredients: formData.ingredients
          .split(",")
          .map((i: string) => i.trim())
          .filter(Boolean),
        dermatologically_safe: true,
        recommended_for: [],
      };

      const response = await fetch(`${API_BASE}/api/v1/products`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
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
        setTimeout(() => setSuccessMessage(null), 3000);
        await fetchProducts();
      } else {
        const data = await response.json();
        setError(data.detail || "Failed to add product");
      }
    } catch (err: any) {
      setError(err?.message || "Error adding product");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full py-8 md:py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 dark:from-blue-400 dark:to-cyan-400 bg-clip-text text-transparent mb-2">
            Admin - Product Recommendations
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Manage products and recommendations
          </p>
        </div>

        {/* Success Message */}
        {successMessage && (
          <div className="mb-6 p-4 bg-green-100 dark:bg-green-900/30 border-l-4 border-green-600 dark:border-green-400 rounded-lg flex items-start gap-3">
            <span className="text-2xl flex-shrink-0">✅</span>
            <div>
              <p className="font-semibold text-green-800 dark:text-green-200">
                Success
              </p>
              <p className="text-green-700 dark:text-green-300 text-sm">
                {successMessage}
              </p>
            </div>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-100 dark:bg-red-900/30 border-l-4 border-red-600 dark:border-red-400 rounded-lg flex items-start gap-3">
            <span className="text-2xl flex-shrink-0">⚠️</span>
            <div>
              <p className="font-semibold text-red-800 dark:text-red-200">
                Error
              </p>
              <p className="text-red-700 dark:text-red-300 text-sm">{error}</p>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Add Product Form */}
          <div className="bg-white/80 dark:bg-white/10 backdrop-blur-md rounded-xl shadow-lg p-8 border border-white/20 dark:border-white/10 h-fit">
            <h2 className="text-2xl font-bold text-gray-800 dark:text-white mb-6">
              ➕ Add New Product
            </h2>
            <form onSubmit={handleAddProduct} className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">
                  Product Name
                </label>
                <input
                  type="text"
                  name="name"
                  placeholder="e.g., CeraVe Moisturizer"
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-slate-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-600 dark:focus:ring-blue-400 focus:border-transparent"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">
                  Brand
                </label>
                <input
                  type="text"
                  name="brand"
                  placeholder="e.g., CeraVe"
                  value={formData.brand}
                  onChange={(e) =>
                    setFormData({ ...formData, brand: e.target.value })
                  }
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-slate-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-600 dark:focus:ring-blue-400 focus:border-transparent"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">
                  Category
                </label>
                <select
                  name="category"
                  value={formData.category}
                  onChange={(e) =>
                    setFormData({ ...formData, category: e.target.value })
                  }
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-slate-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-600 dark:focus:ring-blue-400 focus:border-transparent"
                >
                  <option value="cleanser">Cleanser</option>
                  <option value="moisturizer">Moisturizer</option>
                  <option value="serum">Serum</option>
                  <option value="treatment">Treatment</option>
                  <option value="sunscreen">Sunscreen</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">
                  Tags (comma-separated)
                </label>
                <textarea
                  name="tags"
                  placeholder="e.g., hydrating, gentle, dermatologist-tested"
                  value={formData.tags}
                  onChange={(e) =>
                    setFormData({ ...formData, tags: e.target.value })
                  }
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-slate-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-600 dark:focus:ring-blue-400 focus:border-transparent resize-none"
                  rows={2}
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">
                  Ingredients (comma-separated)
                </label>
                <textarea
                  name="ingredients"
                  placeholder="e.g., Ceramides, Hyaluronic Acid, Glycerin"
                  value={formData.ingredients}
                  onChange={(e) =>
                    setFormData({ ...formData, ingredients: e.target.value })
                  }
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-slate-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-600 dark:focus:ring-blue-400 focus:border-transparent resize-none"
                  rows={2}
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-3 px-4 rounded-lg transition shadow-lg"
              >
                {loading ? "Adding..." : "✨ Add Product"}
              </button>
            </form>
          </div>

          {/* Products List */}
          <div className="bg-white/80 dark:bg-white/10 backdrop-blur-md rounded-xl shadow-lg p-8 border border-white/20 dark:border-white/10">
            <h2 className="text-2xl font-bold text-gray-800 dark:text-white mb-6">
              📦 Products ({products.length})
            </h2>

            {loading && !products.length && (
              <div className="text-center py-8">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 dark:border-blue-400"></div>
                <p className="text-gray-600 dark:text-gray-300 mt-3">
                  Loading products...
                </p>
              </div>
            )}

            {products.length === 0 && !loading && (
              <div className="text-center py-8">
                <p className="text-gray-500 dark:text-gray-400">
                  No products yet. Add one to get started!
                </p>
              </div>
            )}

            <div className="space-y-3 max-h-[70vh] overflow-y-auto">
              {products.map((p) => (
                <div
                  key={p.id}
                  className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 bg-gray-50 dark:bg-slate-800/50 hover:bg-gray-100 dark:hover:bg-slate-800 transition"
                >
                  <h3 className="font-bold text-gray-900 dark:text-white">
                    {p.name}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                    {p.brand}{" "}
                    <span className="inline-block px-2 py-1 bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300 rounded text-xs font-semibold ml-2">
                      {p.category}
                    </span>
                  </p>
                  {p.tags?.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {p.tags.map((tag) => (
                        <span
                          key={tag}
                          className="inline-block px-2 py-1 bg-cyan-100 dark:bg-cyan-900/50 text-cyan-700 dark:text-cyan-300 rounded text-xs"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                  {p.ingredients?.length > 0 && (
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                      Ingredients: {p.ingredients.join(", ")}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
