# Anomaly Report

- Scored rows: 96
- Rows needing review: 3
- Injected events: 4
- Injected events flagged: 3

## Highest Scored Rows

| timestamp | mode | score | top signal | injected event |
| --- | --- | ---: | --- | --- |
| 2026-01-01T07:50:00+00:00 | eclipse | 19.027 | gyro_rate_dps | attitude control disturbance |
| 2026-01-01T12:10:00+00:00 | sunlit | 6.145 | bus_voltage | voltage sag |
| 2026-01-01T14:40:00+00:00 | eclipse | 4.073 | downlink_snr_db | downlink fade |
| 2026-01-01T14:10:00+00:00 | sunlit | 1.657 | gyro_rate_dps |  |
| 2026-01-01T09:50:00+00:00 | sunlit | 1.644 | gyro_rate_dps |  |
| 2026-01-01T11:20:00+00:00 | eclipse | 1.600 | gyro_rate_dps |  |
| 2026-01-01T00:20:00+00:00 | sunlit | 1.593 | gyro_rate_dps |  |
| 2026-01-01T02:10:00+00:00 | sunlit | 1.574 | gyro_rate_dps |  |

Scores use robust distance from the median. The report is meant to
surface rows for review, not to automate an operational decision.
