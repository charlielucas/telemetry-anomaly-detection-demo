# Anomaly Report

- Scored rows: 96
- Rows needing review: 3
- Injected events: 4
- Injected events flagged: 3

## Highest Scored Rows

| timestamp | mode | score | top signal | injected event |
| --- | --- | ---: | --- | --- |
| 2026-01-01T07:50:00+00:00 | eclipse | 28.210 | gyro_rate_dps | attitude control disturbance |
| 2026-01-01T12:10:00+00:00 | sunlit | 9.110 | bus_voltage | voltage sag |
| 2026-01-01T14:40:00+00:00 | eclipse | 6.038 | downlink_snr_db | downlink fade |
| 2026-01-01T14:10:00+00:00 | sunlit | 2.457 | gyro_rate_dps |  |
| 2026-01-01T09:50:00+00:00 | sunlit | 2.438 | gyro_rate_dps |  |
| 2026-01-01T11:20:00+00:00 | eclipse | 2.371 | gyro_rate_dps |  |
| 2026-01-01T00:20:00+00:00 | sunlit | 2.362 | gyro_rate_dps |  |
| 2026-01-01T02:10:00+00:00 | sunlit | 2.333 | gyro_rate_dps |  |

Scores use robust distance from the median. The report is meant to
surface rows for review, not to automate an operational decision.
