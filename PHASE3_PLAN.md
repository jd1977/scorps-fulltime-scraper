# Phase 3: Maintainability Improvements

## Goals
- Break down large monolithic functions
- Add comprehensive type hints
- Standardize naming conventions
- Improve code readability

## Large Functions to Refactor

### complete_social_media_agent.py

1. **create_fixtures_post()** (~200 lines)
   - Extract: `_draw_fixture_item()`
   - Extract: `_calculate_fixtures_overlay()`
   - Extract: `_load_post_fonts()`

2. **create_results_post()** (~240 lines)
   - Extract: `_draw_result_item()`
   - Extract: `_calculate_results_overlay()`
   - Extract: `_draw_form_guide()`

3. **create_weekly_results_post()** (~170 lines)
   - Extract: `_draw_weekly_result_item()`
   - Extract: `_calculate_weekly_overlay()`

4. **create_table_post()** (~240 lines)
   - Extract: `_draw_table_row()`
   - Extract: `_draw_table_headers()`
   - Extract: `_calculate_table_overlay()`

### scorpions_social_media_menu.py

1. **show_fixtures_by_team()** (~100 lines)
   - Already uses agent methods, minimal refactoring needed

2. **show_results_by_team()** (~150 lines)
   - Extract scraping logic to agent
   - Simplify display logic

## Type Hints to Add

- All function parameters
- All return types
- Class attributes
- Complex data structures (use TypedDict or dataclasses)

## Naming Standardization

### Current Issues:
- Mix of `get_team_data()` vs `create_fixtures_post()`
- Some private methods use `_scrape_` prefix, others don't

### Standard:
- Public methods: `verb_noun()` (get_data, create_post, fetch_results)
- Private methods: `_verb_noun()` (_parse_html, _draw_item, _calculate_size)
- Boolean methods: `is_` or `has_` prefix (is_scorps_team, has_results)

## Implementation Order

1. **Font Loading** (Quick Win)
   - Create `_load_post_fonts()` method
   - Use in all post creation methods

2. **Overlay Calculations** (Medium)
   - Extract overlay size calculations
   - Reuse across post types

3. **Drawing Functions** (Large)
   - Extract item drawing logic
   - Make testable and reusable

4. **Type Hints** (Throughout)
   - Add as we refactor each function
   - Use typing module for complex types

5. **Naming Cleanup** (Final)
   - Rename inconsistent methods
   - Update all references

## Expected Benefits

- **Testability**: Smaller functions easier to unit test
- **Readability**: Clear, focused functions
- **Reusability**: Common logic extracted
- **Maintainability**: Easier to modify and debug
- **IDE Support**: Better autocomplete with type hints
