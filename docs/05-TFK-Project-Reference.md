# TFK Project Reference — Store Facts & Working Notes

*Quick-reference file for the Operations, Sales & Brand Performance project. Only the TFK Shopify store is used in this project.*

## Store Setup

| Item | Value |
|---|---|
| Store name | The Fragrance Kitchen |
| Domain | www.tfk.com.kw |
| Platform | Shopify — Advanced plan (full ShopifyQL analytics available) |
| Currency | KWD (3 decimal places) |
| Timezone | UTC+3 (Kuwait) — all reporting in Kuwait time |
| Country | Kuwait |
| Store contact | reach@tfk.com.kw |
| Site languages | English, Arabic, French |
| Markets | Kuwait (primary), UAE pages |
| Web developer | WAVE (wavemena.com) |
| Parent company | Development Holding Company (dhc.com.kw) |

## Catalog Snapshot (verified live via Shopify Admin API, July 13, 2026)

- 46 active products; 67 items in the All Fragrance collection
- 7 collections, counts confirmed exact against Product Catalog Reference (see that doc for structure and the Signature/Exclusive handle mismatch)
- Price ladder: 25 → 30 → 35 → 60 → 75 KWD (+60–90 KWD trio sets, 20–125 KWD gift cards) — 30 KWD (The Finest) previously undocumented, now added
- Single-variant products (100ml) dominate; mists at 50ml

## Project Scope

1. **Sales performance** — revenue, orders, AOV, top products, customer mix (new vs returning), period comparisons via ShopifyQL.
2. **Operations** — inventory health, sell-through, stockouts/negative stock, bundle inventory sync, SKU/product-type hygiene, fulfillment.
3. **Brand & social** — traffic and conversion by referral source, social-attributed revenue, campaign performance, consistency with brand guidelines.

## Open Items / Known Issues to Investigate

- [x] Bundle products showing negative inventory — reverified live July 13: figures unchanged (Mist Affair -19, Some Like It Bloom P&M -8, Son of a Rose P&M -14, Fly Me to the Rose P&M -5, Rose Frequency -4, Afterlight Accord -7, Quiet Bloom -1, Radiant Veil -2); still needs bundle-component inventory sync fix
- [ ] THE FINEST at 2 units (30 KWD, distinct product from The Finest Everyday) — restock or retire?
- [ ] Low stock: N.8 Remix (41), N.33 Remix (86)
- [ ] Missing SKUs and product types on 2025–2026 launches — data hygiene for analytics; also found Abdul Rashid using a placeholder SKU (`00000`)
- [ ] Confirm meaning and consistency of the "24h" product tag (confirmed live on 15 of 46 active products)
- [ ] Obtain official brand assets (exact color codes, fonts) to finalize Brand Guidelines — logo wordmark and two packaging design languages now confirmed via site screenshots (v1.1)
- [ ] Connect/collect social analytics for the social performance workstream
- [ ] Cross-check Marketing/Retail Performance deck figures (39,500 followers, 1,134,730 site visits, 12.2M ad impressions) against live ShopifyQL/GA/social insights before external use
- [ ] Add fragrance notes profiles for catalog items not yet covered in the presentation deck (Petals of Salt, Black Ember, Seventh Sense, Bloom Club, Electric Bloom, Son of a Rose, The Absolute, The Imagination, The Road, L'Extase Blanche)

## Working Conventions

- All figures reported in KWD, Kuwait time.
- "Signature Collection" and "Exclusive Collection" always referenced by title + handle to avoid the naming mismatch.
- Monthly performance reviews to combine: ShopifyQL sales + sessions/conversion + referral-source data + social metrics.

---
*Created July 12, 2026. Catalog and collections figures reverified live via Shopify Admin API July 13, 2026. Update as the project evolves.*
