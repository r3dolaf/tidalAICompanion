# Implementation Plan: SQLite Database Migration

## Goal
Migrate data persistence from ad-hoc JSON files and browser `localStorage` to a robust Server-Side SQLite database (`tidal.db`). This ensures:
1.  **Data Safety:** No data loss if browser cache is cleared.
2.  **Scalability:** Support for thousands of patterns.
3.  **Portability:** Single `.db` file to backup.

## 1. Database Schema
We will use `sqlite3` (standard library) with a wrapper class. Use a single file `raspberry-pi/tidal.db`.

### Tables

#### `patterns_history`
Stores every generated pattern.
- `id` (INTEGER PK AUTOINCREMENT)
- `pattern` (TEXT)
- `style` (TEXT)
- `density` (REAL)
- `complexity` (REAL)
- `tempo` (INTEGER)
- `timestamp` (DATETIME DEFAULT CURRENT_TIMESTAMP)
- `is_favorite` (BOOLEAN DEFAULT 0)
- `metadata` (JSON TEXT) -- For extra fields like thoughts, layers, mood

#### `favorites`
Stores explicitly saved patterns (Linked to history or standalone? Standalone is safer for now).
- `id` (INTEGER PK AUTOINCREMENT)
- `pattern` (TEXT)
- `name` (TEXT) -- User defined or auto-generated
- `tags` (TEXT) -- Comma separated
- `created_at` (DATETIME)

#### `presets`
Stores knob configurations.
- `id` (INTEGER PK AUTOINCREMENT)
- `name` (TEXT)
- `config_json` (TEXT) -- Dump of knob values

## 2. Backend Changes (`raspberry-pi/web/`)

### 2.1 New File: `database.py`
- `init_db()`: Create tables if not exists.
- `DatabaseManager` class:
    - `add_history_entry(data)`
    - `get_history(limit=50)`
    - `add_favorite(pattern, metadata)`
    - `get_favorites()`
    - `delete_favorite(id)`

### 2.2 Update `app.py`
- Initialize `DatabaseManager` in `AppState`.
- Update `/api/generate`: calling `db.add_history_entry()` after successful generation.
- Update `/api/favorites`: Read/Write from DB instead of `favorites.json`.
- **New Endpoint:** `/api/history`: To fetch server-side history (replacing localStorage logic).

### 2.3 Migration Script: `migrate_data.py`
- Read existing `favorites.json`.
- Insert into `favorites` table.
- (Optional) Read client-side history if sent by user? (Too complex, assume fresh start for history or let user manually import).

## 3. Frontend Changes

### 3.1 History Manager (`js/modules/history.js`?)
- Remove `localStorage` logic for patterns.
- Add `fetchHistory()` triggering persistent API call.
- Update UI to render history from server response.

## 4. Execution Steps
1.  Create `database.py`.
2.  Integrate into `app.py`.
3.  Migrate `favorites.json` data.
4.  Update Frontend to use `/api/history`.
5.  Verify persistence.
