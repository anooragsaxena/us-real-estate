PRAGMA foreign_keys = ON;

-- Canonical properties and most recent observed listing data.
CREATE TABLE IF NOT EXISTS listings (
    id INTEGER PRIMARY KEY,
    source TEXT NOT NULL CHECK (source IN ('Zillow','Redfin')),
    url TEXT NOT NULL UNIQUE CHECK (url LIKE 'https://%'),
    address TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL CHECK (state IN ('AZ','NV','WA','OR','ID')),
    zip_code TEXT,
    bedrooms INTEGER NOT NULL CHECK (bedrooms IN (2,3)),
    bathrooms REAL NOT NULL,
    property_type TEXT NOT NULL DEFAULT 'detached_sfh' CHECK (property_type = 'detached_sfh'),
    asking_price_usd REAL NOT NULL CHECK (asking_price_usd > 0),
    finished_sqft REAL CHECK (finished_sqft > 0),
    year_built INTEGER CHECK (year_built BETWEEN 1700 AND 2100),
    listing_status TEXT NOT NULL DEFAULT 'active'
        CHECK (listing_status IN ('active','pending','sold','off_market','unknown')),
    observed_on TEXT NOT NULL,
    notes TEXT NOT NULL DEFAULT '',
    CHECK ((bedrooms = 2 AND bathrooms = 2) OR (bedrooms = 3 AND bathrooms >= 2))
);

-- Historical changes must not overwrite past price observations.
CREATE TABLE IF NOT EXISTS price_observations (
    id INTEGER PRIMARY KEY,
    listing_id INTEGER NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
    observed_on TEXT NOT NULL,
    asking_price_usd REAL NOT NULL CHECK (asking_price_usd > 0),
    listing_status TEXT NOT NULL,
    source_url TEXT NOT NULL,
    notes TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS rental_comps (
    id INTEGER PRIMARY KEY,
    listing_id INTEGER NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
    address TEXT NOT NULL,
    bedrooms INTEGER NOT NULL,
    bathrooms REAL NOT NULL,
    asking_rent_usd REAL NOT NULL CHECK (asking_rent_usd > 0),
    source_url TEXT NOT NULL CHECK (source_url LIKE 'https://%'),
    observed_on TEXT NOT NULL,
    notes TEXT NOT NULL DEFAULT ''
);

-- Sale comps are CLOSED transactions only; never enter active/pending ask prices.
CREATE TABLE IF NOT EXISTS sale_comps (
    id INTEGER PRIMARY KEY,
    listing_id INTEGER NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
    address TEXT NOT NULL,
    sold_price_usd REAL NOT NULL CHECK (sold_price_usd > 0),
    sold_on TEXT NOT NULL,
    bedrooms INTEGER NOT NULL CHECK (bedrooms > 0),
    bathrooms REAL NOT NULL CHECK (bathrooms > 0),
    finished_sqft REAL NOT NULL CHECK (finished_sqft > 0),
    year_built INTEGER CHECK (year_built BETWEEN 1700 AND 2100),
    distance_miles REAL NOT NULL CHECK (distance_miles >= 0),
    source_url TEXT NOT NULL CHECK (source_url LIKE 'https://%'),
    observed_on TEXT NOT NULL,
    sale_verified INTEGER NOT NULL DEFAULT 0 CHECK (sale_verified IN (0,1)),
    verification_url TEXT,
    transaction_type TEXT NOT NULL DEFAULT 'unknown'
       CHECK (transaction_type IN ('arm_length','distressed','unknown')),
    condition_relation TEXT NOT NULL DEFAULT 'unknown'
       CHECK (condition_relation IN ('similar','better','worse','unknown')),
    notes TEXT NOT NULL DEFAULT ''
);

-- Evidence-based red flags, not automatically asserted defects or repair estimates.
CREATE TABLE IF NOT EXISTS findings (
    id INTEGER PRIMARY KEY,
    listing_id INTEGER NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
    category TEXT NOT NULL CHECK (
       category IN ('condition','location','title','insurance','leasing','market','other')
    ),
    severity TEXT NOT NULL CHECK (severity IN ('low','medium','high','critical')),
    evidence_status TEXT NOT NULL CHECK (evidence_status IN ('suspected','confirmed')),
    resolution TEXT NOT NULL DEFAULT 'open' CHECK (resolution IN ('open','resolved')),
    description TEXT NOT NULL,
    estimated_cost_usd REAL CHECK (estimated_cost_usd >= 0),
    evidence_url TEXT,
    observed_on TEXT NOT NULL,
    notes TEXT NOT NULL DEFAULT ''
);

-- JSON preserves the complete scenario as modeled, enabling later reproduction.
CREATE TABLE IF NOT EXISTS assessments (
    id INTEGER PRIMARY KEY,
    listing_id INTEGER NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
    assessed_at TEXT NOT NULL DEFAULT (datetime('now')),
    scenario TEXT NOT NULL,
    inputs_json TEXT NOT NULL,
    results_json TEXT NOT NULL,
    rent_comp_count INTEGER NOT NULL,
    screen_status TEXT NOT NULL CHECK (screen_status IN ('WATCH','REVIEW')),
    notes TEXT NOT NULL DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_listings_market ON listings(state, city);
CREATE INDEX IF NOT EXISTS idx_rental_comps_listing ON rental_comps(listing_id);
CREATE INDEX IF NOT EXISTS idx_assessments_listing ON assessments(listing_id, id DESC);
CREATE INDEX IF NOT EXISTS idx_observations_listing ON price_observations(listing_id, id DESC);
CREATE INDEX IF NOT EXISTS idx_sale_comps_listing ON sale_comps(listing_id, sold_on DESC);
CREATE INDEX IF NOT EXISTS idx_findings_listing ON findings(listing_id, resolution);
