export type Language = "en" | "es";
export type SectionKey = "generation" | "interconnectors" | "coverage" | "system" | "method";
export interface SourceRow { key: string; url: string; last_update: string | null }
export interface SeriesRow { period: string; series: string; value: number; share: number }
export interface PriceRow { period: string; price_es_eur_mwh: number; periods: number }
export interface ExchangeRow { period: string; country: string; direction: "import" | "export"; value_gwh: number }
export interface HourlyFile { year: number; path: string; sha256: string; bytes: number; rows: number; missing_by_column: Record<string, number> }
export interface HourlyShard {
  schema_version: number; year: number; timezone: "Europe/Madrid"; unit: "MW";
  geography: { geo_id: number; name: string }; columns: string[];
  rows: Array<Array<string | number | null>>; missing_by_column: Record<string, number>;
}
export interface DashboardData {
  schema_version: number; generated_at: string;
  geography: { generation: string; hourly: string };
  generation: SeriesRow[]; demand: SeriesRow[]; capacity: SeriesRow[]; emissions_context: SeriesRow[];
  exchanges: ExchangeRow[]; storage_energy: SeriesRow[]; storage_capacity: SeriesRow[];
  hourly: { status: "unavailable" | "configured" | "available"; reason?: string; years: number[]; start_utc?: string; end_utc?: string; columns?: string[]; files?: HourlyFile[]; provisional?: boolean };
  omie_prices: PriceRow[];
  marginal_technology: { cutoff: string; status: string; rows: Array<{ timestamp: string; technology: string }> };
  sources: SourceRow[];
}
export interface Manifest {
  schema_version: number; generated_at: string;
  dashboard: { path: string; sha256: string; bytes: number };
  coverage: { monthly_start: string | null; monthly_end: string | null; hourly_status: string; hourly_start?: string | null; hourly_end?: string | null };
  hourly?: { files: HourlyFile[] };
}
