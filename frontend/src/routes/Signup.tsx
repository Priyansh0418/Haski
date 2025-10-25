import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/useAuth";

const MIN_PASSWORD_LENGTH = 8;
const PASSWORD_REGEX = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/;

export default function Signup() {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [apiError, setApiError] = useState("");
  const [success, setSuccess] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [touched, setTouched] = useState<Record<string, boolean>>({});
  const { signup } = useAuth();
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
        if (value.length < MIN_PASSWORD_LENGTH) {
          return `Password must be at least ${MIN_PASSWORD_LENGTH} characters`;
        }
        if (!PASSWORD_REGEX.test(value)) {
          return "Password must contain uppercase, lowercase, and number";
        }
        return "";

      case "confirmPassword":
        if (!value) return "Please confirm your password";
        if (value !== formData.password) {
          return "Passwords do not match";
        }
        return "";

      default:
        return "";
    }
  };

  // Validate all fields
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    Object.keys(formData).forEach((key) => {
      const error = validateField(key, formData[key as keyof typeof formData]);
      if (error) newErrors[key] = error;
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle field changes
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
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

    const error = validateField(name, formData[name as keyof typeof formData]);
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
      // Extract email and password from form data
      // Note: The signup function takes (email, username, password)
      // We'll use email as username since the form simplified fields
      await signup(
        formData.email,
        formData.email.split("@")[0],
        formData.password
      );

      setSuccess("✅ Account created successfully! Redirecting...");

      // Brief delay to show success message
      setTimeout(() => {
        navigate("/dashboard");
      }, 500);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Signup failed";

      // Check for specific error conditions
      if (errorMsg.includes("already") || errorMsg.includes("registered")) {
        setApiError(
          "This email is already registered. Try logging in instead."
        );
      } else if (errorMsg.includes("Invalid")) {
        setApiError("Invalid input. Please check your email and try again.");
      } else {
        setApiError(errorMsg);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const isFormValid =
    formData.email &&
    formData.password &&
    formData.confirmPassword &&
    Object.keys(errors).length === 0;

  return (
    <div className="w-full min-h-screen flex items-center justify-center p-4 py-12">
      <div className="bg-white/80 dark:bg-slate-800/50 backdrop-blur-sm rounded-2xl shadow-xl p-6 sm:p-8 w-full max-w-md border border-gray-100 dark:border-slate-700 hover:shadow-2xl transition-all duration-300">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl sm:text-4xl font-black text-center bg-gradient-to-r from-blue-600 to-cyan-600 dark:from-blue-400 dark:to-cyan-400 bg-clip-text text-transparent mb-2">
            Sign Up
          </h1>
          <p className="text-center text-slate-600 dark:text-slate-400 font-medium">
            Create your Haski account
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
              {apiError.includes("already") && (
                <Link
                  to="/login"
                  className="text-red-700 dark:text-red-300 hover:text-red-900 dark:hover:text-red-100 text-xs mt-1 font-semibold underline"
                >
                  Go to login →
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
              value={formData.email}
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
            <label
              htmlFor="password"
              className="block text-sm font-bold text-slate-900 dark:text-white mb-2"
            >
              Password
            </label>
            <input
              id="password"
              type="password"
              name="password"
              value={formData.password}
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
                  : "password-hint"
              }
              required
            />
            {errors.password && touched.password ? (
              <p
                id="password-error"
                className="text-red-600 dark:text-red-400 text-sm mt-1 flex items-center gap-1"
              >
                <span>✗</span> {errors.password}
              </p>
            ) : !touched.password ? (
              <p
                id="password-hint"
                className="text-slate-500 dark:text-slate-400 text-xs mt-1"
              >
                Min 8 chars: uppercase, lowercase, and number
              </p>
            ) : null}
          </div>

          {/* Confirm Password Field */}
          <div>
            <label
              htmlFor="confirmPassword"
              className="block text-sm font-bold text-slate-900 dark:text-white mb-2"
            >
              Confirm Password
            </label>
            <input
              id="confirmPassword"
              type="password"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              onBlur={handleBlur}
              className={`w-full border-2 rounded-xl px-4 py-3 focus:ring-2 focus:outline-none transition bg-white dark:bg-slate-700 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 ${
                errors.confirmPassword && touched.confirmPassword
                  ? "border-red-500 dark:border-red-400 focus:ring-red-200 dark:focus:ring-red-500/50"
                  : "border-gray-200 dark:border-slate-600 focus:border-blue-500 dark:focus:border-cyan-500 focus:ring-blue-200 dark:focus:ring-cyan-500/50"
              }`}
              placeholder="••••••••"
              aria-label="Confirm password"
              aria-describedby={
                errors.confirmPassword && touched.confirmPassword
                  ? "confirm-error"
                  : undefined
              }
              required
            />
            {errors.confirmPassword && touched.confirmPassword && (
              <p
                id="confirm-error"
                className="text-red-600 dark:text-red-400 text-sm mt-1 flex items-center gap-1"
              >
                <span>✗</span> {errors.confirmPassword}
              </p>
            )}
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading || !isFormValid}
            className="w-full bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 dark:from-blue-700 dark:to-cyan-700 dark:hover:from-blue-800 dark:hover:to-cyan-800 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold py-3 px-4 rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl hover:scale-[1.02] active:scale-[0.98]"
            aria-busy={isLoading}
          >
            {isLoading ? (
              <span className="flex items-center justify-center gap-2">
                <span className="inline-block animate-spin">⏳</span>
                Creating account...
              </span>
            ) : (
              "✨ Create Account"
            )}
          </button>
        </form>

        {/* Footer */}
        <div className="mt-6 pt-6 border-t border-gray-200 dark:border-slate-700">
          <p className="text-center text-slate-700 dark:text-slate-300 text-sm">
            Already have an account?{" "}
            <Link
              to="/login"
              className="text-blue-600 dark:text-cyan-400 hover:text-blue-700 dark:hover:text-cyan-300 font-bold transition"
            >
              Log in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
