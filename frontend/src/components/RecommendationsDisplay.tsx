interface Routine {
  name?: string;
  description?: string;
  steps?: string[];
  frequency?: string;
}

interface Product {
  id?: string | number;
  name?: string;
  category?: string;
  brand?: string;
  description?: string;
  reason?: string;
  link?: string;
  price?: string;
}

interface DietSuggestion {
  food?: string;
  benefits?: string;
  frequency?: string;
  reason?: string;
}

interface RecommendationsData {
  routines?: Routine[];
  products?: Product[];
  recommended_products?: Product[];
  diet_suggestions?: DietSuggestion[];
  diet_recommendations?: DietSuggestion[];
}

interface RecommendationsDisplayProps {
  data: RecommendationsData;
  onClear: () => void;
}

export default function RecommendationsDisplay({
  data,
  onClear,
}: RecommendationsDisplayProps) {
  // Support both old and new API response formats
  const routines = data.routines || [];
  const products = data.recommended_products || data.products || [];
  const diet = data.diet_recommendations || data.diet_suggestions || [];

  const hasContent =
    routines.length > 0 || products.length > 0 || diet.length > 0;

  if (!hasContent) {
    return (
      <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg text-center">
        <p className="text-blue-800">
          No recommendations available at this time.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Disclaimer */}
      <div className="bg-amber-50 border-l-4 border-amber-400 p-4 rounded">
        <p className="text-sm font-semibold text-amber-900">
          ⚠️ Medical Disclaimer
        </p>
        <p className="text-sm text-amber-800 mt-1">
          This information is <strong>informational only</strong> and{" "}
          <strong>not medical advice</strong>. Always consult with a healthcare
          professional or dermatologist before making changes to your routine or
          starting new treatments.
        </p>
      </div>

      {/* Routines Section */}
      {routines && routines.length > 0 && (
        <div>
          <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <span className="text-2xl">🔄</span>
            Recommended Routines
          </h3>
          <div className="grid gap-4">
            {routines.map((routine, idx) => (
              <div
                key={idx}
                className="border-l-4 border-blue-500 bg-blue-50 rounded-lg p-4 hover:shadow-md transition"
              >
                <h4 className="font-semibold text-blue-900 text-lg">
                  {routine.name || `Routine ${idx + 1}`}
                </h4>
                {routine.frequency && (
                  <p className="text-sm text-blue-700 mt-1">
                    <span className="font-medium">Frequency:</span>{" "}
                    {routine.frequency}
                  </p>
                )}
                {routine.description && (
                  <p className="text-sm text-gray-700 mt-2">
                    {routine.description}
                  </p>
                )}
                {routine.steps && routine.steps.length > 0 && (
                  <div className="mt-3">
                    <p className="text-sm font-medium text-gray-700 mb-2">
                      Steps:
                    </p>
                    <ol className="list-decimal list-inside space-y-1">
                      {routine.steps.map((step, stepIdx) => (
                        <li key={stepIdx} className="text-sm text-gray-600">
                          {step}
                        </li>
                      ))}
                    </ol>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Products Section */}
      {products && products.length > 0 && (
        <div>
          <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <span className="text-2xl">🛍️</span>
            Recommended Products
          </h3>
          <div className="grid gap-4 md:grid-cols-2">
            {products.map((product, idx) => (
              <div
                key={idx}
                className="border rounded-lg p-4 bg-gradient-to-br from-green-50 to-emerald-50 hover:shadow-lg transition"
              >
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h4 className="font-semibold text-green-900">
                      {product.name || `Product ${idx + 1}`}
                    </h4>
                    {product.brand && (
                      <p className="text-xs text-green-700">
                        by {product.brand}
                      </p>
                    )}
                  </div>
                  {product.price && (
                    <span className="text-sm font-bold text-green-700 bg-white px-2 py-1 rounded">
                      {product.price}
                    </span>
                  )}
                </div>

                {product.category && (
                  <span className="inline-block bg-green-200 text-green-800 text-xs px-2 py-1 rounded mb-2">
                    {product.category}
                  </span>
                )}

                {product.description && (
                  <p className="text-sm text-gray-700 mb-2">
                    {product.description}
                  </p>
                )}

                {product.reason && (
                  <div className="bg-white rounded p-2 mb-3 border border-green-200">
                    <p className="text-xs text-gray-600">
                      <span className="font-medium">Why:</span> {product.reason}
                    </p>
                  </div>
                )}

                {product.link && (
                  <a
                    href={product.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm font-medium text-green-600 hover:text-green-800 inline-flex items-center gap-1"
                  >
                    View Product →
                  </a>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Diet Suggestions Section */}
      {diet && diet.length > 0 && (
        <div>
          <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <span className="text-2xl">🥗</span>
            Diet Suggestions
          </h3>
          <div className="grid gap-4">
            {diet.map((diet_item, idx) => (
              <div
                key={idx}
                className="border-l-4 border-orange-500 bg-orange-50 rounded-lg p-4 hover:shadow-md transition"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-semibold text-orange-900 text-lg">
                      {diet_item.food || `Food Suggestion ${idx + 1}`}
                    </h4>
                    {diet_item.frequency && (
                      <p className="text-sm text-orange-700 mt-1">
                        <span className="font-medium">Frequency:</span>{" "}
                        {diet_item.frequency}
                      </p>
                    )}
                    {diet_item.benefits && (
                      <p className="text-sm text-gray-700 mt-2">
                        <span className="font-medium">Benefits:</span>{" "}
                        {diet_item.benefits}
                      </p>
                    )}
                    {diet_item.reason && (
                      <p className="text-sm text-gray-700 mt-2">
                        <span className="font-medium">Why:</span>{" "}
                        {diet_item.reason}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-3 pt-4 border-t">
        <button
          onClick={onClear}
          className="flex-1 bg-gray-500 hover:bg-gray-600 text-white font-semibold py-2 rounded-lg transition"
        >
          Clear
        </button>
      </div>
    </div>
  );
}
