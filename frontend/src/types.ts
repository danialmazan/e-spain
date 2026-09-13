export type Language = "en" | "es";
export type SectionKey = "generation" | "interconnectors" | "coverage" | "marginal" | "system";
export interface SourceRow { key: string; url: string; last_update: string | null }
export interface SeriesRow { period: string; series: string; value: number; share: number }
export interface PriceRow { period: string; price_es_eur_mwh: number; periods: number }
export interface ExchangeRow { period: string; country: string; direction: "import" | "export"; value_gwh: number }
export interface DashboardData {
  schema_version: number; generated_at: string;
  geography: { generation: string; hourly: string };
  generation: SeriesRow[]; demand: SeriesRow[]; capacity: SeriesRow[]; emissions_context: SeriesRow[];
  exchanges: ExchangeRow[]; storage_energy: SeriesRow[]; storage_capacity: SeriesRow[];
  hourly: { status: "unavailable" | "configured" | "available"; reason?: string; years: number[] };
  omie_prices: PriceRow[];
  marginal_technology: { cutoff: string; status: string; rows: Array<{ timestamp: string; technology: string }> };
  sources: SourceRow[];
}
export interface Manifest {
  schema_version: number; generated_at: string;
  dashboard: { path: string; sha256: string; bytes: number };
  coverage: { monthly_start: string | null; monthly_end: string | null; hourly_status: string };
}
