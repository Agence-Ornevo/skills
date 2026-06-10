# Power Query M Debugging Patterns — Kings Pastry D02 Session

## Session Context
**Date:** 2026-06-06  
**Project:** Kings Pastry D02 Service & Fulfillment Dashboard  
**Task:** Build UNION tables (SalesHeader_Union, SalesLine_Union) from current + archive tables with proper deduplication

---

## Common Errors & Fixes

### 1. "The import X matches no exports"
**Error:** `Expression.Error: The import ArchiveDeduped matches no exports.`
**Cause:** Referencing a step/query that exists inside another query, not as a separate named query.
**Fix:** Each Power Query can only reference other **named queries** in the Queries pane. Inline the logic or create a separate query.

```powerquery
// BROKEN - ArchiveDeduped is a STEP inside SalesHeader_Union
LatestHeaderVersions = Table.SelectColumns(ArchiveDeduped, ...)

// FIXED - Inline the dedup logic
SourceHeaderArchive = SalesHeaderArchive,
HeaderArchiveSorted = Table.Sort(SourceHeaderArchive, {{"DateArchived", Order.Descending}, {"TimeArchived", Order.Descending}}),
HeaderArchiveGrouped = Table.Group(HeaderArchiveSorted, {"No"}, {{"LatestRow", each Table.FirstN(_, 1), type table}}),
HeaderArchiveDeduped = Table.ExpandTableColumn(HeaderArchiveGrouped, "LatestRow", ...)
```

---

### 2. "Token Eof expected"
**Error:** `Expression.SyntaxError: Token Eof expected.`
**Cause:** Syntax issue — missing closing brace `}`, parenthesis `)`, incomplete statement, or missing `in` clause.
**Fix:** Every `let` must end with `in` + final expression. Check all `{ }`, `[ ]`, `( )` pairs. No trailing commas.

---

### 3. "We cannot convert a value of type Table to type List"
**Error:** `Expression.Error: We cannot convert a value of type Table to type List.`
**Cause:** `Table.Column(Current, "No")` fails because `Current` is not a table (wrong query name, or query not loaded).
**Fix:** Use exact query name from Queries pane. Run debug query to list all names:

```powerquery
let
    Source = #sections[Section1],
    Names = Record.FieldNames(Source),
    Filtered = List.Select(Names, each not Text.StartsWith(_, "#"))
in
    Filtered
```

---

### 4. "The column 'CompositeKey' of the table wasn't found"
**Error:** `Expression.Error: The column 'CompositeKey' of the table wasn't found.`
**Cause:** Created `CompositeKey` on Current table **before** `Table.Combine`. After combining with Archive (which lacks the column), the combined table has no `CompositeKey`.

```powerquery
// BROKEN - Key created BEFORE union
CurrentWithKey = Table.AddColumn(CurrentFiltered, "CompositeKey", ...)
Combined = Table.Combine({CurrentWithKey, ArchiveWithPeriod})  // Archive has no CompositeKey!
// Combined has NO CompositeKey column
```

**Fix:** Create the composite key **AFTER** the union so it exists on all rows:

```powerquery
// FIXED - Key created AFTER union
Combined = Table.Combine({CurrentFiltered, ArchiveWithPeriod})
CombinedWithKey = Table.AddColumn(Combined, "CompositeKey", each [DocumentNo] & "|" & Text.From([LineNo]))
CurrentKeys = Table.Column(Table.SelectRows(CombinedWithKey, each [SourcePeriod] = "Current"), "CompositeKey")
Deduped = Table.SelectRows(CombinedWithKey, each [SourcePeriod] = "Current" or not List.Contains(CurrentKeys, [CompositeKey]))
```

---

## Self-Contained Query Pattern

**Rule:** Make each query self-contained. Inline shared logic rather than referencing other queries' steps.

```powerquery
// GOOD - Self-contained SalesLine_Union includes its own header archive dedup
let
    SourceHeaderArchive = SalesHeaderArchive,
    HeaderArchiveSorted = Table.Sort(...),
    HeaderArchiveDeduped = ...,
    HeaderVersionDates = Table.SelectColumns(HeaderArchiveDeduped, {"No", "DateArchived", "TimeArchived"}),
    // ... rest of logic inline
in
    Cleaned
```

---

## Debug Query — List All Query Names

Run this in a new blank query to see exact names:

```powerquery
let
    Source = #sections[Section1],
    Names = Record.FieldNames(Source),
    Filtered = List.Select(Names, each not Text.StartsWith(_, "#"))
in
    Filtered
```

**Output example:**
```
{"SalesHeader", "SalesHeaderArchive", "SalesLine", "SalesLineArchive", "Item", "ItemCategory", "Customer", "DailyInventorySnapshot", "KPIConfig"}
```

Use **exact names** from this list in your scripts.

---

## Key M Functions Reference

| Function | Purpose |
|----------|---------|
| `Table.SelectRows(table, each condition)` | Filter rows |
| `Table.AddColumn(table, "name", each expr)` | Add calculated column |
| `Table.Combine({table1, table2})` | Union tables |
| `Table.Column(table, "colName")` | Returns **List** of column values |
| `List.Contains(list, value)` | Check if value exists in list |
| `Table.Group(table, {"key"}, {{"agg", each Table.FirstN(_, 1), type table}})` | Keep first row per group |
| `Table.ExpandTableColumn(table, "col", {"subcol1", "subcol2"}, {"new1", "new2"})` | Flatten nested table |
| `Table.NestedJoin(t1, {"key1"}, t2, {"key2"}, "newCol", JoinKind.LeftOuter)` | Left join |
| `Table.Buffer(table)` | Materialize table in memory (prevents re-evaluation) |
| `Table.RemoveColumns(table, {"col1", "col2"})` | Drop columns |

---

## Common Pitfalls Checklist

- [ ] Query names match **exactly** (case-sensitive, spaces need `#"..."`)
- [ ] Source queries have **Enable Load** checked
- [ ] `let` ... `in` structure complete (no missing `in`)
- [ ] No trailing commas in records/lists
- [ ] Composite keys created **after** `Table.Combine`
- [ ] `Table.Column` returns **List**, not Table
- [ ] `each` keyword used in row functions (`Table.SelectRows`, `Table.AddColumn`)
- [ ] Archive deduplication uses `DateArchived` + `TimeArchived` DESC
- [ ] Cross-dedup: prefer Current over Archive
- [ ] Empty PKs filtered in Current tables before UNION