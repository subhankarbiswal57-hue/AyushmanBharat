// Offline Storage & Background Sync Manager for Rural Primary Health Centres (PHCs)
// Persists triage assessments, encounter requests, and ABHA registration in IndexedDB
// Automatically syncs when internet connectivity is restored.

const DB_NAME = "AyushmanOfflineDB";
const DB_VERSION = 1;
const SYNC_STORE = "offline_sync_queue";

class OfflineSyncManager {
  constructor() {
    this.db = null;
    this.isOnline = typeof navigator !== "undefined" ? navigator.onLine : true;
    this._initEvents();
  }

  async openDB() {
    if (this.db) return this.db;
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION);
      request.onupgradeneeded = (e) => {
        const db = e.target.result;
        if (!db.objectStoreNames.contains(SYNC_STORE)) {
          const store = db.createObjectStore(SYNC_STORE, { keyPath: "id", autoIncrement: true });
          store.createIndex("timestamp", "timestamp", { unique: false });
          store.createIndex("status", "status", { unique: false });
        }
      };
      request.onsuccess = (e) => {
        this.db = e.target.result;
        resolve(this.db);
      };
      request.onerror = (e) => reject(e.target.error);
    });
  }

  _initEvents() {
    if (typeof window !== "undefined") {
      window.addEventListener("online", () => {
        this.isOnline = true;
        this.processSyncQueue();
      });
      window.addEventListener("offline", () => {
        this.isOnline = false;
      });
    }
  }

  async enqueueAction(actionType, payload) {
    const db = await this.openDB();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(SYNC_STORE, "readwrite");
      const store = tx.objectStore(SYNC_STORE);
      const item = {
        actionType,
        payload,
        timestamp: Date.now(),
        status: "pending",
        retryCount: 0
      };
      const req = store.add(item);
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
  }

  async getPendingActions() {
    const db = await this.openDB();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(SYNC_STORE, "readonly");
      const store = tx.objectStore(SYNC_STORE);
      const req = store.getAll();
      req.onsuccess = () => {
        const pending = (req.result || []).filter(item => item.status === "pending");
        resolve(pending);
      };
      req.onerror = () => reject(req.error);
    });
  }

  async markActionCompleted(id) {
    const db = await this.openDB();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(SYNC_STORE, "readwrite");
      const store = tx.objectStore(SYNC_STORE);
      const req = store.delete(id);
      req.onsuccess = () => resolve();
      req.onerror = () => reject(req.error);
    });
  }

  async processSyncQueue(apiEndpoint = "/api/v1/sync") {
    if (!this.isOnline) return { synced: 0, message: "Device is currently offline" };
    const items = await this.getPendingActions();
    let syncedCount = 0;

    for (const item of items) {
      try {
        const response = await fetch(apiEndpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            action: item.actionType,
            data: item.payload,
            client_timestamp: item.timestamp
          })
        });

        if (response.ok) {
          await this.markActionCompleted(item.id);
          syncedCount++;
        }
      } catch (err) {
        console.warn(`[OfflineSync] Sync failed for item ${item.id}:`, err);
      }
    }

    return { synced: syncedCount, remaining: items.length - syncedCount };
  }
}

if (typeof window !== "undefined") {
  window.offlineSync = new OfflineSyncManager();
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { OfflineSyncManager };
}
