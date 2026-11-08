-- Q1: latest position of each aircraft (window function ROW_NUMBER)
WITH ranked AS (
    SELECT p.*,
           ROW_NUMBER() OVER (PARTITION BY icao24 ORDER BY ts DESC) AS rn
    FROM positions p
)
SELECT r.icao24, a.callsign, a.country, r.ts, r.lat, r.lon,
       r.altitude_m, r.speed_ms
FROM ranked r
JOIN aircraft a USING (icao24)
WHERE r.rn = 1
ORDER BY r.ts DESC;

-- Q2: change in altitude/speed between consecutive readings (LAG)
SELECT icao24, ts, altitude_m,
       altitude_m - LAG(altitude_m) OVER w AS alt_change_m,
       speed_ms - LAG(speed_ms) OVER w AS speed_change_ms,
       EXTRACT(EPOCH FROM (ts - LAG(ts) OVER w)) AS seconds_since_prev
FROM positions
WINDOW w AS (PARTITION BY icao24 ORDER BY ts)
ORDER BY icao24, ts
LIMIT 15;

-- Q3: aircraft and readings per country (GROUP BY)
SELECT a.country,
       COUNT(DISTINCT p.icao24) AS aircraft_seen,
       COUNT(*) AS readings
FROM positions p
JOIN aircraft a USING (icao24)
GROUP BY a.country
ORDER BY aircraft_seen DESC;

-- Q4: flight path of the aircraft with the most readings (CTE)
WITH busiest AS (
    SELECT icao24
    FROM positions
    GROUP BY icao24
    ORDER BY COUNT(*) DESC
    LIMIT 1
)
SELECT p.icao24, p.ts, p.lat, p.lon, p.altitude_m
FROM positions p
JOIN busiest b USING (icao24)
ORDER BY p.ts
LIMIT 15;

-- Q5: traffic over time, 10-minute buckets (date_bin)
SELECT date_bin('10 minutes', ts, TIMESTAMPTZ '2026-01-01 00:00:00+00') AS bucket,
       COUNT(DISTINCT icao24) AS aircraft
FROM positions
GROUP BY bucket
ORDER BY bucket;