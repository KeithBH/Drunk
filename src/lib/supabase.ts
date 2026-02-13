import Constants from "expo-constants";
import { createClient } from "@supabase/supabase-js";

const extra = Constants.expoConfig?.extra ?? {};
const supabaseUrl = extra.supabaseUrl as string;
const supabaseAnonKey = extra.supabaseAnonKey as string;

if (!supabaseUrl || !supabaseAnonKey) {
  console.warn("Missing Supabase config. Set SUPABASE_URL and SUPABASE_ANON_KEY in env.");
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true
  }
});

export const edgeBaseUrl = (extra.edgeFunctionBaseUrl as string) || "";
