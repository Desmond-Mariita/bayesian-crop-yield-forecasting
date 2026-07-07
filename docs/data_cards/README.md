# Data cards — authoring notes

Every dataset gets a card (`DC-<slug>.md`) before code consumes it (LINV-005). Cards are
validated in CI by `tools/check_data_cards.py`. Copy an existing card as a template.

## Restricted frontmatter syntax (not real YAML)

The checker parses a deliberate subset: `key: value` scalars and block lists
(`key:` followed by `  - item` lines). Nested mappings, block scalars, anchors, and
multi-line values are unsupported — simplify the card instead.

**Footgun — spaces before `#`:** the parser treats whitespace-then-`#` as an inline
comment start. `source_url: https://example.com/page#section` is safe;
`source_url: https://example.com/page #section` silently loses ` #section`. Never put a
space before `#` inside a value.

Required scalar fields: `dataset_id`, `dataset_name`, `version`, `status`
(`draft`/`approved`), `data_source_tag`, `source_url`, `collection_method`,
`date_range`, `geographic_scope`, `temporal_resolution`, `phase`.
Required non-empty lists: `known_limitations`, `intended_use` (no empty items).
