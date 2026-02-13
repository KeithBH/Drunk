export default ({ config }) => ({
  ...config,
  name: "Drunk",
  slug: "drunk",
  scheme: "drunk",
  version: "0.1.0",
  orientation: "portrait",
  icon: "./assets/icon.png",
  userInterfaceStyle: "light",
  splash: {
    image: "./assets/splash.png",
    resizeMode: "contain",
    backgroundColor: "#F6F1E8"
  },
  assetBundlePatterns: ["**/*"],
  ios: {
    supportsTablet: true
  },
  android: {
    adaptiveIcon: {
      foregroundImage: "./assets/adaptive-icon.png",
      backgroundColor: "#F6F1E8"
    }
  },
  extra: {
    supabaseUrl: process.env.SUPABASE_URL || "",
    supabaseAnonKey: process.env.SUPABASE_ANON_KEY || "",
    edgeFunctionBaseUrl: process.env.SUPABASE_EDGE_BASE_URL || ""
  }
});
