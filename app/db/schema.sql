CREATE TABLE IF NOT EXISTS aircraft (
    icao24   VARCHAR(10) PRIMARY KEY,
    callsign VARCHAR(20),
    country  VARCHAR(60)
);

CREATE TABLE IF NOT EXISTS positions (
    id            BIGSERIAL PRIMARY KEY,
    icao24        VARCHAR(10) NOT NULL REFERENCES aircraft(icao24),
    ts            TIMESTAMPTZ NOT NULL,
    lat           DOUBLE PRECISION,
    lon           DOUBLE PRECISION,
    altitude_m    REAL,
    speed_ms      REAL,
    heading       REAL,
    vertical_rate REAL,
    on_ground     BOOLEAN,
    squawk        VARCHAR(4),
    UNIQUE (icao24, ts)
);
CREATE INDEX IF NOT EXISTS idx_pos_icao_ts ON positions (icao24, ts);

CREATE TABLE IF NOT EXISTS airports (
    code VARCHAR(4) PRIMARY KEY,
    name TEXT,
    lat  DOUBLE PRECISION,
    lon  DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS routes (
    from_code   VARCHAR(4) REFERENCES airports(code),
    to_code     VARCHAR(4) REFERENCES airports(code),
    distance_km REAL,
    PRIMARY KEY (from_code, to_code)
);

CREATE TABLE IF NOT EXISTS alerts (
    id      SERIAL PRIMARY KEY,
    icao24  VARCHAR(10) REFERENCES aircraft(icao24),
    type    VARCHAR(30),
    ts      TIMESTAMPTZ,
    details TEXT
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_alerts_dedupe ON alerts (icao24, type, ts);