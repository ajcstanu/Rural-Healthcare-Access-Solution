/**
 * frontend/src/utils/i18n.ts
 *
 * React-i18next initialisation for NabhaHealth.
 *
 * Translation JSON files are managed by Intlayer (intlayer.config.ts at repo
 * root).  Intlayer does NOT change the runtime — it only keeps the JSON files
 * up-to-date via the CLI / CI pipeline.
 *
 * To add a new key:
 *   1. Add it to frontend/src/i18n/en.json  (English source of truth)
 *   2. Run:  npx intlayer fill              (auto-translates pa + hi)
 *   3. Commit the updated JSON files
 *
 * Supported AI providers for `intlayer fill`:
 *   --provider openai    (default, needs INTLAYER_API_KEY)
 *   --provider anthropic (needs INTLAYER_API_KEY)
 *   --provider ollama    (free, runs locally — great for offline dev)
 */

import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import HttpBackend from "i18next-http-backend";
import LanguageDetector from "i18next-browser-languagedetector";

// ---------------------------------------------------------------------------
// Supported locales — keep in sync with intlayer.config.ts
// ---------------------------------------------------------------------------
export const SUPPORTED_LOCALES = ["en", "pa", "hi"] as const;
export type Locale = (typeof SUPPORTED_LOCALES)[number];

i18n
  // Load translations at runtime from /locales/<lng>/<ns>.json
  // (populated and kept in sync by Intlayer)
  .use(HttpBackend)

  // Auto-detect user language from browser / localStorage / querystring
  .use(LanguageDetector)

  // Pass the i18n instance into react-i18next
  .use(initReactI18next)

  .init({
    // Fallback if detected language is not supported
    fallbackLng: "en",

    // Available languages — Intlayer ensures these files are always complete
    supportedLngs: SUPPORTED_LOCALES,

    // Namespace strategy — one file per feature area keeps bundles small
    defaultNS: "common",
    ns: ["common", "consultation", "medicines", "records", "symptomChecker"],

    backend: {
      // Intlayer's syncJSON writes to this same path
      loadPath: "/locales/{{lng}}/{{ns}}.json",
    },

    detection: {
      // Prefer Punjabi for users in Punjab; fall back to browser header
      order: ["localStorage", "navigator", "htmlTag"],
      caches: ["localStorage"],
    },

    interpolation: {
      // React already escapes values; no double-escaping needed
      escapeValue: false,
    },

    // Log missing keys in development so Intlayer can catch them in CI
    saveMissing: process.env.NODE_ENV === "development",
    missingKeyHandler: (lngs, ns, key) => {
      console.warn(`[i18n] Missing key "${ns}:${key}" for [${lngs.join(", ")}]`);
    },
  });

export default i18n;
