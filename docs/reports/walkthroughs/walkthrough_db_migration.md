# Database Migration Walkthrough

## Overview
Replaced the file-based (`favorites.json`) and client-side (`localStorage`) persistence model with a robust Server-Side SQLite database (`tidal.db`). This ensures data safety and scalability.

## Architecture
- **Database**: `raspberry-pi/tidal.db` (SQLite)
- **Manager**: `raspberry-pi/web/database.py` (Handles connections and queries)
- **API**: Updated `/api/favorites`, added `/api/history`, `/api/data/import`.

## Changes

### 1. Backend (`raspberry-pi/web/`)
- **New File**: [`database.py`](file:///C:/Users/alfredo/Desktop/tidalai-companion/raspberry-pi/web/database.py)
    - Defines `history` and `favorites` tables.
    - Provides methods: `add_history_entry`, `get_history`, `add_favorite`, `import_client_data`.
- **Modified**: [`app.py`](file:///C:/Users/alfredo/Desktop/tidalai-companion/raspberry-pi/web/app.py)
    - Initialized `DatabaseManager`.
    - Updated specific endpoints to use the DB.
    - Added migration endpoint.

### 2. Frontend (`raspberry-pi/web/static/js/`)
- **Modified**: [`main.js`](file:///C:/Users/alfredo/Desktop/tidalai-companion/raspberry-pi/web/static/js/main.js)
    - Added `checkDataMigration()`: Checks for legacy `localStorage` data and sends it to the server.
    - Display visible "Toast" notifications during migration.
- **Modified**: [`panels.js`](file:///C:/Users/alfredo/Desktop/tidalai-companion/raspberry-pi/web/static/js/ui/panels.js)
    - Updated `loadMorphOptions` to fetch History/Favorites from the API instead of `localStorage`.

## Deployment
Run `deploy.bat` to push the new structure. The database file will be created automatically on the Raspberry Pi upon first run.

## Validation
1.  **Migration**: On first load, the browser will show "📦 Migrando datos...".
2.  **Persistence**: Generated patterns appear in `/api/history`.
3.  **Safety**: Clearing browser cache does NOT lose data.
