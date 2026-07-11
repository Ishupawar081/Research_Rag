import { useEffect } from "react";
import { Routes, Route, Navigate, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "./contexts/AuthContext";
import LandingPage from "./pages/Landing/LandingPage";
import Auth from "./pages/Auth";
import Dashboard from "./pages/Dashboard";
import MainLayout from "./layout/MainLayout";
import Profile from "./pages/Profile";
import Settings from "./pages/Settings";

import AuthCallback from "./pages/AuthCallback";

const RequireAuth = ({ children }) => {
  const { session } = useAuth();
  if (!session) return <Navigate to="/auth" replace />;
  return children;
};

const GuestOnly = ({ children }) => {
  const { session } = useAuth();
  if (session) return <Navigate to="/dashboard" replace />;
  return children;
};

export default function App() {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    // Intercept Supabase auth callbacks on any route if they have standard auth hash parameters
    const hash = location.hash;
    const search = location.search;
    
    if (hash && (hash.includes('access_token=') || hash.includes('error=') || hash.includes('type=recovery') || hash.includes('type=signup'))) {
      if (location.pathname !== '/auth/callback') {
        navigate(`/auth/callback${hash}`, { replace: true });
      }
    } else if (search && (search.includes('error=') || search.includes('error_code='))) {
      if (location.pathname !== '/auth/callback') {
        navigate(`/auth/callback${search}`, { replace: true });
      }
    }
  }, [location, navigate]);

  return (
    <Routes>
      <Route path="/" element={<GuestOnly><LandingPage /></GuestOnly>} />
      <Route path="/auth" element={<GuestOnly><Auth /></GuestOnly>} />
      <Route path="/auth/callback" element={<AuthCallback />} />
      <Route path="/dashboard" element={<RequireAuth><Dashboard /></RequireAuth>} />
      <Route path="/profile" element={<RequireAuth><Profile /></RequireAuth>} />
      <Route path="/settings" element={<RequireAuth><Settings /></RequireAuth>} />
      <Route path="/workspace/:chatId?" element={<RequireAuth><MainLayout /></RequireAuth>} />
    </Routes>
  );
}