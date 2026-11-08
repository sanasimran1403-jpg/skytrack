EMERGENCY_SQUAWKS = {
    "7500": "hijacking",
    "7600": "radio failure",
    "7700": "general emergency",
}


def check_squawk(reading):
    code = reading.get("squawk")
    if code in EMERGENCY_SQUAWKS:
        return {
            "icao24": reading["icao24"],
            "type": "emergency_squawk",
            "ts": reading["ts"],
            "details": f"squawk {code} ({EMERGENCY_SQUAWKS[code]})",
        }
    return None