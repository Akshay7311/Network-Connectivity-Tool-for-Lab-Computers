import { useNavigate } from "react-router-dom";
import { Shield } from "lucide-react";
import { LoginForm } from "../components/auth/LoginForm";

export function LoginPage() {
  const navigate = useNavigate();

  const handleLogin = async (email: string, password: string) => {
    // Mock login - in a real app, this would call an API
    if (email && password) {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000));
      localStorage.setItem("isAuthenticated", "true");
      navigate("/dashboard");
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center">
          <Shield className="w-12 h-12 text-blue-600" />
        </div>
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          NetScan Login
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          Sign in to access your network scanning dashboard
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <LoginForm onSubmit={handleLogin} />
        </div>
      </div>
    </div>
  );
}
