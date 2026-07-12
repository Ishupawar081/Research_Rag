import axios from "axios";
import { supabase } from "../lib/supabase";

export const api = axios.create({
    baseURL: import.meta.env.VITE_BACKEND_URL || "http://127.0.0.1:8000"
});

api.interceptors.request.use(async (config) => {
    const { data: { session } } = await supabase.auth.getSession();
    if (session?.access_token) {
        config.headers.Authorization = `Bearer ${session.access_token}`;
    }
    return config;
});

export async function chat(data) {
    // Use a generous timeout for LLM calls running on CPU.
    // - Single/Collection queries can take 1-2 min on CPU.
    // - Comparison (3 LLM calls) can take 4-6 min on CPU.
    const TIMEOUT_MS = 600000; // 10 minutes

    try {
        const res = await api.post("/chat", data, { timeout: TIMEOUT_MS });
        return res.data;
    } catch (error) {
        if (error.code === 'ECONNABORTED') {
            // Explicit axios timeout
            return {
                success: false,
                error: "The LLM is taking too long to respond (exceeded 10 minutes). " +
                       "Try a simpler question or restart Ollama."
            };
        }

        if (!error.response) {
            // Network-level failure — could be connection refused, DNS, or the server crashed
            if (error.code === 'ERR_NETWORK' || error.message?.includes('Network Error')) {
                return {
                    success: false,
                    error: "Cannot reach the backend server. " +
                           "Make sure the FastAPI server is running on port 8000."
                };
            }
            // Connection was reset while waiting (common when request takes very long)
            return {
                success: false,
                error: "The connection to the backend was interrupted. " +
                       "The LLM may still be processing — please wait a moment and try again."
            };
        }

        // Server returned a proper HTTP error response
        return {
            success: false,
            error: error.response?.data?.error || "An unexpected server error occurred."
        };
    }
}