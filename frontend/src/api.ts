import type { DashboardData, HourlyShard, Manifest } from "./types";

async function readJson<T>(path: string): Promise<T> {
  const response = await fetch(`${import.meta.env.BASE_URL}data/${path}`, { cache: "no-cache" });
  if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
  return response.json() as Promise<T>;
}

export async function loadDashboard() {
  const manifest = await readJson<Manifest>("manifest.json");
  const dashboard = await readJson<DashboardData>(manifest.dashboard.path);
  if (manifest.schema_version !== 1 || dashboard.schema_version !== 1) throw new Error("Unsupported data schema");
  return { manifest, dashboard };
}

const hourlyCache = new Map<number, Promise<HourlyShard>>();

export async function loadHourlyYears(years: number[]) {
  return Promise.all(years.map((year) => {
    let pending = hourlyCache.get(year);
    if (!pending) {
      pending = readJson<HourlyShard>(`hourly/${year}.json`).then((shard) => {
        if (shard.schema_version !== 1 || shard.year !== year) throw new Error(`Unsupported hourly shard: ${year}`);
        return shard;
      });
      hourlyCache.set(year, pending);
    }
    return pending;
  }));
}
