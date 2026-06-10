# Kings Pastry — NULL PromisedDeliveryDate Business Rule

**Policy change (commit 785076e, 2026-06-09):** When an order has no promised delivery date, treat the shipment as **on-time by default**, but still enforce **In-Full** for OTIF compliance.

## Rule (SQL Form)

### OTIF — on-time IF no promise, but In-Full still required
```sql
-- IsOTIFCompliant: NULL Promised => treat as on-time; In-Full ENFORCED
CASE
    WHEN sl.DocumentNo IS NOT NULL
     AND sl.Quantity IS NOT NULL
     AND sl.Quantity > 0
     AND sl.ShipmentDate IS NOT NULL
     AND (sl.PromisedDeliveryDate IS NULL OR sl.ShipmentDate <= sl.PromisedDeliveryDate)
     AND sl.QuantityShipped >= sl.Quantity
    THEN 1 ELSE 0
END AS IsOTIFCompliant
```

### On-Time — any shipment is compliant when no promise exists
```sql
-- IsOnTimeCompliant: NULL Promised => compliant
CASE
    WHEN sl.DocumentNo IS NOT NULL
     AND sl.ShipmentDate IS NOT NULL
     AND (sl.PromisedDeliveryDate IS NULL OR sl.ShipmentDate <= sl.PromisedDeliveryDate)
    THEN 1 ELSE 0
END AS IsOnTimeCompliant
```

### Eligible — no longer requires PromisedDeliveryDate
```sql
CASE
    WHEN sl.DocumentNo IS NOT NULL
     AND sl.Quantity IS NOT NULL
     AND sl.Quantity > 0
     AND sl.ShipmentDate IS NOT NULL
    THEN 1 ELSE 0
END AS IsEligible
```

### Late flag — only fires when a promise existed and was missed
```sql
CASE
    WHEN sl.DocumentNo IS NOT NULL
     AND sl.ShipmentDate IS NOT NULL
     AND sl.PromisedDeliveryDate IS NOT NULL
     AND sl.ShipmentDate > sl.PromisedDeliveryDate
    THEN 1 ELSE 0
END AS IsLate
```

## KPI Impact Matrix

| KPI | Uses PromisedDeliveryDate | Rule Applied | KPI Effect |
|-----|---------------------------|--------------|------------|
| **OTIF %** | Yes | NULL = on-time, In-Full still enforced | Eligibles 52.7K → 192K, % 36.4% → 34.3% |
| **On-Time %** | Yes | NULL = on-time | Eligibles 52.9K → 192K, % 97.7% → 99.4% |
| **Fill Rate %** | No (uses Qty only) | N/A | No change |
| **ReqPromAdh %** | Yes (Promised vs Requested) | **UNCHANGED — exclusion preserved** | No change |
| **Stockout FG/Ing %** | No (inventory snapshot) | N/A | No change |

## Why ReqPromAdh Is Excluded

ReqPromAdh compares **Promised vs Requested** to answer: *"Did we keep our promise to the customer?"* A NULL Promised date means there was no promise — the adherence question is meaningless. If NULLs were counted as compliant, teams could game the metric by simply not entering promised dates.

**Rule of thumb:** When in doubt, ask *"what business question does this KPI answer?"* before applying NULL-tolerance.
- **Fulfillment KPIs** (OTIF, On-Time) → NULL promise = default on-time
- **Commitment KPIs** (ReqPromAdh) → NULL = exclusion

## Files Affected

- `D02_Service_Fulfillment/SQL_views/03_v_D02_OTIF_Daily.sql` (IsEligible, IsOTIFCompliant, IsLate)
- `D02_Service_Fulfillment/SQL_views/04_v_D02_OnTime_Daily.sql` (IsEligible, IsOnTimeCompliant, IsLate)
- `D02_Service_Fulfillment/SQL_views/v_D02_OTIF_Detail.sql` (IsOnTime, IsOTIF)

**NOT touched (intentionally):** `05_v_D02_FillRate_Daily.sql`, `06_v_D02_ReqPromAdh_Daily.sql`, `07_v_D02_Stockout_Daily.sql`.

## Verification Query

```sql
SELECT COUNT(*) AS total_rows,
    SUM(IsEligible) AS eligible,
    SUM(IsOTIFCompliant) AS compliant,
    100.0 * SUM(IsOTIFCompliant) / NULLIF(SUM(IsEligible), 0) AS otif_pct,
    SUM(CASE WHEN PromisedDeliveryDate IS NULL AND IsEligible = 1 THEN 1 ELSE 0 END) AS eligible_via_null
FROM pbi.v_D02_OTIF_Daily
```

Expected: `eligible_via_null` ≈ 139K (all formerly-excluded NULL-promise rows now participate).

## Post-Change KPI Targets

New baseline numbers for KPI cards (refresh after deploy):
- **OTIF %**: ~34.3% (target 95% → shows red chip until ops improves)
- **On-Time %**: ~99.4% (target 90% → shows green chip)

⚠️ The 95% OTIF target was calibrated against the old 27%-eligible subset, not the full 192K population. Flag as a conversation to raise with stakeholders.

## Traceability

- Commit: `785076e`
- Session: 2026-06-09 (freelance-data profile)
- User directive: *"lets g with the defaults"* — choosing to apply NULL-tolerance to OTIF/OnTime, In-Full still enforced, ReqPromAdh unchanged.
