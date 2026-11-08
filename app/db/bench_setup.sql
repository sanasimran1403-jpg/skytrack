DROP TABLE IF EXISTS positions_bench;

CREATE TABLE positions_bench (
    id         BIGSERIAL PRIMARY KEY,
    icao24     VARCHAR(10) NOT NULL,
    ts         TIMESTAMPTZ NOT NULL,
    lat        DOUBLE PRECISION,
    lon        DOUBLE PRECISION,
    altitude_m REAL,
    speed_ms   REAL
);

-- 2000 aircraft x 500 readings each = 1,000,000 rows
INSERT INTO positions_bench (icao24, ts, lat, lon, altitude_m, speed_ms)
SELECT
    'bench' || lpad((g % 2000)::text, 5, '0'),
    TIMESTAMPTZ '2026-11-01 00:00:00+00' + (g / 2000) * INTERVAL '30 seconds',
    12 + random() * 9,
    74 + random() * 9,
    random() * 12000,
    100 + random() * 200
FROM generate_series(0, 999999) AS g;

ANALYZE positions_bench;