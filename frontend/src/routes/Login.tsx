import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/useAuth";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [apiError, setApiError] = useState("");
  const [success, setSuccess] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [touched, setTouched] = useState<Record<string, boolean>>({});
  const { login } = useAuth();
  const navigate = useNavigate();

  // Client-side validation
  const validateField = (name: string, value: string): string => {
    switch (name) {
      case "email":
        if (!value) return "Email is required";
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
          return "Please enter a valid email address";
        }
        return "";

      case "password":
        if (!value) return "Password is required";
        if (value.length < 1) return "Password is required";
        return "";

      default:
        return "";
    }
  };

  // Validate all fields
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    Object.keys({ email, password }).forEach((key) => {
      const error = validateField(key, key === "email" ? email : password);
      if (error) newErrors[key] = error;
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle field changes
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    if (name === "email") setEmail(value);
    if (name === "password") setPassword(value);
    setApiError("");
    setSuccess("");

    // Real-time validation for touched fields
    if (touched[name]) {
      const error = validateField(name, value);
      setErrors((prev) => {
        if (error) {
          return { ...prev, [name]: error };
        } else {
          const { [name]: _, ...rest } = prev;
          return rest;
        }
      });
    }
  };

  // Handle field blur for touched state
  const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    const { name } = e.target;
    setTouched((prev) => ({ ...prev, [name]: true }));

    const error = validateField(name, name === "email" ? email : password);
    setErrors((prev) => {
      if (error) {
        return { ...prev, [name]: error };
      } else {
        const { [name]: _, ...rest } = prev;
        return rest;
      }
    });
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setApiError("");
    setSuccess("");

    // Validate form
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);
    try {
      await login(email, password);
      setSuccess("✅ Login successful! Redirecting...");

      // Brief delay to show success message
      setTimeout(() => {
        navigate("/dashboard");
      }, 500);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Login failed";

      // Check for specific error conditions
      if (errorMsg.includes("401") || errorMsg.includes("Unauthorized")) {
        setApiError("Invalid email or password. Please check and try again.");
      } else if (
        errorMsg.includes("not found") ||
        errorMsg.includes("not registered")
      ) {
        setApiError(
          "No account found with this email. Try signing up instead."
        );
      } else if (errorMsg.includes("network") || errorMsg.includes("Network")) {
        setApiError(
          "Network error. Please check your connection and try again."
        );
      } else {
        setApiError(errorMsg);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full min-h-screen flex items-center justify-center p-4 py-12">
      <div className="bg-white/80 dark:bg-slate-800/50 backdrop-blur-sm rounded-2xl shadow-xl p-6 sm:p-8 w-full max-w-md border border-gray-100 dark:border-slate-700 hover:shadow-2xl transition-all duration-300">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl sm:text-4xl font-black text-center bg-gradient-to-r from-blue-600 to-cyan-600 dark:from-blue-400 dark:to-cyan-400 bg-clip-text text-transparent mb-2">
            Login
          </h1>
          <p className="text-center text-slate-600 dark:text-slate-400 font-medium">
            Welcome back to Haski
          </p>
        </div>

        {/* Success Message */}
        {success && (
          <div className="mb-6 p-4 bg-green-100 dark:bg-green-900/30 border-l-4 border-green-600 dark:border-green-400 rounded-lg flex items-start gap-3">
            <span className="text-2xl flex-shrink-0">✅</span>
            <div>
              <p className="font-semibold text-green-800 dark:text-green-200 text-sm">
                {success}
              </p>
            </div>
          </div>
        )}

        {/* API Error Message */}
        {apiError && (
          <div className="mb-6 p-4 bg-red-100 dark:bg-red-900/30 border-l-4 border-red-600 dark:border-red-400 rounded-lg flex items-start gap-3">
            <span className="text-2xl flex-shrink-0">⚠️</span>
            <div>
              <p className="font-semibold text-red-800 dark:text-red-200 text-sm">
                {apiError}
              </p>
              {apiError.includes("not registered") && (
                <Link
                  to="/signup"
                  className="text-red-700 dark:text-red-300 hover:text-red-900 dark:hover:text-red-100 text-xs mt-1 font-semibold underline"
                >
                  Create an account →
                </Link>
              )}
            </div>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-5" noValidate>
          {/* Email Field */}
          <div>
            <label
              htmlFor="email"
              className="block text-sm font-bold text-slate-900 dark:text-white mb-2"
            >
              Email Address
            </label>
            <input
              id="email"
              type="email"
              name="email"
              value={email}
              onChange={handleChange}
              onBlur={handleBlur}
              className={`w-full border-2 rounded-xl px-4 py-3 focus:ring-2 focus:outline-none transition bg-white dark:bg-slate-700 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 ${
                errors.email && touched.email
                  ? "border-red-500 dark:border-red-400 focus:ring-red-200 dark:focus:ring-red-500/50"
                  : "border-gray-200 dark:border-slate-600 focus:border-blue-500 dark:focus:border-cyan-500 focus:ring-blue-200 dark:focus:ring-cyan-500/50"
              }`}
              placeholder="your@email.com"
              aria-label="Email address"
              aria-describedby={
                errors.email && touched.email ? "email-error" : undefined
              }
              required
            />
            {errors.email && touched.email && (
              <p
                id="email-error"
                className="text-red-600 dark:text-red-400 text-sm mt-1 flex items-center gap-1"
              >
                <span>✗</span> {errors.email}
              </p>
            )}
          </div>

          {/* Password Field */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label
                htmlFor="password"
                className="block text-sm font-bold text-slate-900 dark:text-white"
              >
                Password
              </label>
              <Link
                to="#"
                className="text-xs text-blue-600 dark:text-cyan-400 hover:text-blue-700 dark:hover:text-cyan-300 font-semibold transition"
              >
                Forgot?
              </Link>
            </div>
            <input
              id="password"
              type="password"
              name="password"
              value={password}
              onChange={handleChange}
              onBlur={handleBlur}
              className={`w-full border-2 rounded-xl px-4 py-3 focus:ring-2 focus:outline-none transition bg-white dark:bg-slate-700 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 ${
                errors.password && touched.password
                  ? "border-red-500 dark:border-red-400 focus:ring-red-200 dark:focus:ring-red-500/50"
                  : "border-gray-200 dark:border-slate-600 focus:border-blue-500 dark:focus:border-cyan-500 focus:ring-blue-200 dark:focus:ring-cyan-500/50"
              }`}
              placeholder="••••••••"
              aria-label="Password"
              aria-describedby={
                errors.password && touched.password
                  ? "password-error"
                  : undefined
              }
              required
            />
            {errors.password && touched.password && (
              <p
                id="password-error"
                className="text-red-600 dark:text-red-400 text-sm mt-1 flex items-center gap-1"
              >
                <span>✗</span> {errors.password}
              </p>
            )}
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading || !email || !password}
            className="w-full bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 dark:from-blue-700 dark:to-cyan-700 dark:hover:from-blue-800 dark:hover:to-cyan-800 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold py-3 px-4 rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl hover:scale-[1.02] active:scale-[0.98]"
            aria-busy={isLoading}
          >
            {isLoading ? (
              <span className="flex items-center justify-center gap-2">
                <span className="inline-block animate-spin">⏳</span>
                Logging in...
              </span>
            ) : (
              "🔓 Login"
            )}
          </button>
        </form>

        {/* Footer */}
        <div className="mt-6 pt-6 border-t border-gray-200 dark:border-slate-700">
          <p className="text-center text-slate-700 dark:text-slate-300 text-sm">
            Don't have an account?{" "}
            <Link
              to="/signup"
              className="text-blue-600 dark:text-cyan-400 hover:text-blue-700 dark:hover:text-cyan-300 font-bold transition"
            >
              Sign up now
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
