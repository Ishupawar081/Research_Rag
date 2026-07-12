import { createClient } from "@supabase/supabase-js";

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

console.log("URL =", JSON.stringify(supabaseUrl));
console.log("URL length =", supabaseUrl?.length);

console.log("KEY length =", supabaseAnonKey?.length);
console.log("KEY =", JSON.stringify(supabaseAnonKey));

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error("Missing Supabase configuration");
}

export const supabase = createClient(
  supabaseUrl,
  supabaseAnonKey
);