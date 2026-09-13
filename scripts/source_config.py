"""Pinned public-source configuration for E-Spain."""

REDATA_BASE = "https://apidatos.ree.es/es/datos"
OMIE_DOWNLOAD = "https://www.omie.es/en/file-download"
ESIOS_BASE = "https://api.esios.ree.es"

REDATA_WIDGETS = {
    "generation": "generacion/estructura-generacion",
    "demand": "demanda/evolucion",
    "capacity": "generacion/potencia-instalada-generacion",
    "emissions_context": "generacion/evolucion-estructura-generacion-emisiones-asociadas",
}

REDATA_EXCHANGE_WIDGETS = {
    "France": "intercambios/francia-frontera",
    "Portugal": "intercambios/portugal-frontera",
    "Morocco": "intercambios/marruecos-frontera",
    "Andorra": "intercambios/andorra-frontera",
}

REDATA_STORAGE_WIDGETS = {
    "storage_energy": "almacenamiento/energia-almacenamiento",
    "storage_capacity": "almacenamiento/potencia-instalada-almacenamiento",
}

# These are REE's peninsular, measured-real-time indicators. The ingestion
# validates the returned indicator title and unit before accepting data.
ESIOS_INDICATORS = {
    "demand": {"id": 1293, "expected": "Demanda real"},
    "hydro": {"id": 546, "expected": "hidráulica"},
    "coal": {"id": 547, "expected": "carbón"},
    "fuel_gas": {"id": 548, "expected": "fuel"},
    "nuclear": {"id": 549, "expected": "nuclear"},
    "combined_cycle": {"id": 550, "expected": "combinado"},
    "wind": {"id": 551, "expected": "eólica"},
    "solar_thermal": {"id": 1294, "expected": "térmica"},
    "solar_pv": {"id": 1295, "expected": "fotovoltaica"},
    "cogeneration": {"id": 1296, "expected": "cogeneración"},
    "other": {"id": 1297, "expected": "resto"},
    "portugal": {"id": 10044, "expected": "Portugal"},
    "france": {"id": 10045, "expected": "Francia"},
    "morocco": {"id": 10046, "expected": "Marruecos"},
    "andorra": {"id": 10047, "expected": "Andorra"},
}

PENINSULAR_GEO_ID = 8741
MARGINAL_TECHNOLOGY_CUTOFF = "2025-03-18T23:00:00+01:00"
