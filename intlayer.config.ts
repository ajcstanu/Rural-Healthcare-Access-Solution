/**
 * intlayer.config.ts — NabhaHealth
 *
 * Intlayer sits on TOP of our existing i18next setup.
 * It reads the three locale JSON files we already have and writes
 * AI-filled / synced translations back to the same files.
 *
 * No changes are required to the react-i18next runtime — it keeps
 * loading translations exactly as before from frontend/src/i18n/*.json.
 *
 * To fill missing translations automatically run:
 *   npx intlayer fill --api-key $OPENAI_API_KEY        (OpenAI)
 *   npx intlayer fill --provider anthropic --api-key $ANTHROPIC_API_KEY
 *   npx intlayer fill --provider ollama               (local, free)
 */

import { Locales, type IntlayerConfig } from "intlayer";
import { loadJSON, syncJSON } from "@intlayer/sync-json-plugin";

const config: IntlayerConfig = {
  // ─── Supported locales ────────────────────────────────────────────────────
  internationalization: {
    locales: [
      Locales.ENGLISH,   // en
      Locales.PUNJABI,   // pa  — primary rural language
      Locales.HINDI,     // hi
    ],
    defaultLocale: Locales.ENGLISH,
  },

  // ─── AI translation provider (override via env) ───────────────────────────
  // Set INTLAYER_AI_PROVIDER and INTLAYER_API_KEY in your .env
  // Supported: "openai" | "anthropic" | "ollama" (free, no key needed)
  ai: {
    provider: (process.env.INTLAYER_AI_PROVIDER as any) ?? "openai",
    apiKey: process.env.INTLAYER_API_KEY,
    model: process.env.INTLAYER_AI_MODEL,
  },

  // ─── Plugins ──────────────────────────────────────────────────────────────
  plugins: [
    /**
     * loadJSON — treat the existing i18next JSON files as the source of truth.
     *
     * Pattern: frontend/src/i18n/<locale>.json
     * Intlayer will parse each file and register its keys as dictionaries.
     * The `locale` field tells Intlayer which language these keys belong to.
     *
     * We load EN first (priority 1) so it acts as the reference language
     * that Intlayer uses when auto-translating PA / HI.
     */
    loadJSON({
      // key == locale code (en | pa | hi)
      source: ({ key }) => `./frontend/src/i18n/${key}.json`,
      locale: Locales.ENGLISH,  // reference language
      priority: 1,
      format: "i18next",
    }),

    /**
     * syncJSON — write Intlayer's merged & AI-filled dictionaries back to the
     * same JSON files that react-i18next already loads at runtime.
     *
     * After running `npx intlayer fill`, the pa.json and hi.json files will
     * have every missing key translated automatically.
     */
    syncJSON({
      format: "i18next",
      source: ({ key, locale }) => `./frontend/src/i18n/${locale}/${key}.json`,
      priority: 0,
    }),
  ],
};

export default config;
