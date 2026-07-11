import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Box, Typography, Button, TextField, Container, Card, CardContent } from "@mui/material";
import { supabase } from "../lib/supabase";
import SpaceBackground from "./Landing/SpaceBackground";
import { useAuth } from "../contexts/AuthContext";

export default function AuthCallback() {
    const navigate = useNavigate();
    const location = useLocation();
    const { session } = useAuth();
    
    const [status, setStatus] = useState("processing"); // processing, error, expired, verified
    const [message, setMessage] = useState("Verifying your authentication...");
    const [resendEmail, setResendEmail] = useState("");
    const [resendStatus, setResendStatus] = useState("");
    
    useEffect(() => {
        const processCallback = async () => {
            const hash = location.hash;
            const search = location.search;
            
            let params = new URLSearchParams();
            if (hash) {
                // Supabase typically uses hash fragments for OAuth and email verification
                params = new URLSearchParams(hash.substring(1));
            } else if (search) {
                params = new URLSearchParams(search);
            }
            
            // 6. Never leave raw URL fragments like #error=... visible to the user.
            window.history.replaceState(null, '', window.location.pathname);
            
            const error = params.get("error");
            const errorCode = params.get("error_code");
            const errorDescription = params.get("error_description");
            const type = params.get("type"); 
            const accessToken = params.get("access_token");
            
            if (error || errorCode) {
                if (error === "access_denied" && errorCode === "otp_expired") {
                    // It's ambiguous from the URL alone whether it's truly expired or already verified.
                    // We prompt them for their email to resend, and if it's verified, we will catch it.
                    setStatus("expired");
                    setMessage("Verification link expired.");
                } else {
                    setStatus("error");
                    setMessage(errorDescription?.replace(/\+/g, ' ') || error || "An authentication error occurred.");
                }
            } else if (accessToken) {
                // 5. If verification succeeds: Redirect to Login or Workspace depending on session state.
                // 7. Add an Auth Callback component that handles all Supabase authentication redirects, including: password reset, Google OAuth
                if (type === "recovery") {
                    // Password reset flow
                    navigate("/settings", { replace: true });
                } else {
                    // Email verification or OAuth success
                    if (session) {
                        navigate("/dashboard", { replace: true });
                    } else {
                        navigate("/auth", { replace: true });
                    }
                }
            } else {
                // No parameters found, just redirect based on session
                if (session) {
                    navigate("/dashboard", { replace: true });
                } else {
                    navigate("/auth", { replace: true });
                }
            }
        };
        
        // Slight delay to allow AuthContext to initialize session if it exists
        const timer = setTimeout(() => {
            processCallback();
        }, 500);

        return () => clearTimeout(timer);
    }, [location, navigate, session]);
    
    const handleResend = async () => {
        if (!resendEmail) {
            setResendStatus("Please enter your email.");
            return;
        }
        
        try {
            setResendStatus("Sending...");
            const { error } = await supabase.auth.resend({
                type: 'signup',
                email: resendEmail,
                options: {
                    emailRedirectTo: window.location.origin + '/auth/callback'
                }
            });
            
            if (error) {
                // 3. If the account is already verified: Display "Your email has already been verified. Please sign in."
                if (error.message.toLowerCase().includes("already verified") || error.status === 422) {
                    setStatus("verified");
                    setMessage("Your email has already been verified. Please sign in.");
                    setResendStatus("");
                } else {
                    throw error;
                }
            } else {
                setResendStatus("Verification email sent! Please check your inbox.");
            }
        } catch (err) {
            setResendStatus(err.message);
        }
    };
    
    return (
        <Box sx={{
            position: "relative",
            width: "100%",
            minHeight: "100vh",
            display: "flex",
            bgcolor: "#0B1120",
            color: "white",
            alignItems: "center",
            justifyContent: "center"
        }}>
            <Box sx={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0, zIndex: 0, display: { xs: "none", md: "block" } }}>
                <SpaceBackground />
            </Box>
            
            <Container maxWidth="sm" sx={{ zIndex: 10 }}>
                <Card sx={{ 
                    bgcolor: "rgba(30,41,59,0.7)", 
                    backdropFilter: "blur(20px)",
                    border: "1px solid rgba(255,255,255,0.1)",
                    borderRadius: 4,
                    boxShadow: "0 25px 50px -12px rgba(0,0,0,0.5)"
                }}>
                    <CardContent sx={{ p: { xs: 3, sm: 6 }, textAlign: "center" }}>
                        <Typography variant="h5" sx={{ fontWeight: 700, mb: 2, color: "white" }}>
                            Authentication
                        </Typography>
                        
                        <Typography sx={{ color: "#94A3B8", mb: 4 }}>
                            {message}
                        </Typography>
                        
                        {/* 4. If the verification link truly expired before use: Display "Verification link expired." Add a button "Resend verification email." */}
                        {status === "expired" && (
                            <Box sx={{ mt: 2 }}>
                                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                                    <TextField 
                                        placeholder="Enter your email to resend link" 
                                        variant="outlined"
                                        size="small"
                                        value={resendEmail}
                                        onChange={(e) => setResendEmail(e.target.value)}
                                        sx={{
                                            "& .MuiOutlinedInput-root": {
                                                bgcolor: "rgba(0,0,0,0.2)",
                                                color: "white",
                                                "& fieldset": { borderColor: "rgba(255,255,255,0.1)" },
                                                "&:hover fieldset": { borderColor: "rgba(255,255,255,0.2)" },
                                                "&.Mui-focused fieldset": { borderColor: "#A78BFA" }
                                            }
                                        }}
                                    />
                                    <Button 
                                        onClick={handleResend}
                                        sx={{
                                            background: "linear-gradient(135deg, rgba(139,92,246,0.9) 0%, rgba(59,130,246,0.9) 100%)",
                                            color: "white",
                                            textTransform: "none",
                                            "&:hover": { background: "linear-gradient(135deg, rgba(139,92,246,1) 0%, rgba(59,130,246,1) 100%)" }
                                        }}
                                    >
                                        Resend verification email
                                    </Button>
                                    {resendStatus && (
                                        <Typography sx={{ color: resendStatus.includes("sent") ? "#4ADE80" : "#FCA5A5", fontSize: "0.85rem", mt: 1 }}>
                                            {resendStatus}
                                        </Typography>
                                    )}
                                </Box>
                            </Box>
                        )}
                        
                        {(status === "error" || status === "verified" || status === "expired") && (
                            <Button 
                                fullWidth
                                onClick={() => navigate("/auth")}
                                sx={{
                                    mt: 4,
                                    py: 1.5,
                                    bgcolor: "white", color: "#0F172A",
                                    fontWeight: 600, textTransform: "none",
                                    borderRadius: 2,
                                    "&:hover": { bgcolor: "#F8FAFC" }
                                }}
                            >
                                Go to Sign In
                            </Button>
                        )}
                    </CardContent>
                </Card>
            </Container>
        </Box>
    );
}
