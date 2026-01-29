package db

import (
	"database/sql"
	"fmt"
	"os"
	"path/filepath"
	"time"

	_ "github.com/mattn/go-sqlite3"

	"kclone-go/pkg/state"
)

const schema = `
CREATE TABLE IF NOT EXISTS state_store (
  id TEXT PRIMARY KEY,
  data TEXT
);

CREATE TABLE IF NOT EXISTS nodes (
  id TEXT PRIMARY KEY,
  ip_address TEXT,
  total_cpu INTEGER,
  total_ram INTEGER,
  status TEXT,
  labels TEXT
);

CREATE TABLE IF NOT EXISTS pods (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uid TEXT UNIQUE,
  name TEXT,
  namespace TEXT,
  node_id TEXT,
  image TEXT,
  desired_status TEXT,
  current_status TEXT,
  cpu_request INTEGER,
  mem_request INTEGER,
  labels TEXT
);

CREATE TABLE IF NOT EXISTS services (
  name TEXT PRIMARY KEY,
  cluster_ip TEXT,
  selector TEXT,
  port INTEGER,
  target_port INTEGER
);

CREATE TABLE IF NOT EXISTS replica_sets (
  name TEXT PRIMARY KEY,
  selector TEXT,
  replicas_count INTEGER,
  pod_template TEXT
);
`

func InitDB(path string) error {
	dir := filepath.Dir(path)
	if err := os.MkdirAll(dir, 0o755); err != nil {
		return err
	}
	db, err := sql.Open("sqlite3", path)
	if err != nil {
		return err
	}
	defer db.Close()
	if _, err := db.Exec(schema); err != nil {
		return fmt.Errorf("init schema: %w", err)
	}
	return nil
}

// SaveState writes the full JSON-serialized ClusterState into the DB (single-row store)
func SaveState(cs *state.ClusterState, path string) error {
	if err := InitDB(path); err != nil {
		return err
	}
	db, err := sql.Open("sqlite3", path)
	if err != nil {
		return err
	}
	defer db.Close()

	data := cs.ToJSON()

	tx, err := db.Begin()
	if err != nil {
		return err
	}
	defer tx.Rollback()

	if _, err := tx.Exec(`INSERT INTO state_store(id, data) VALUES(?, ?) ON CONFLICT(id) DO UPDATE SET data = excluded.data`, "cluster", string(data)); err != nil {
		return fmt.Errorf("write state: %w", err)
	}
	if err := tx.Commit(); err != nil {
		return err
	}
	return nil
}

// LoadState loads the ClusterState JSON from the DB and deserializes it
func LoadState(path string) (*state.ClusterState, error) {
	if err := InitDB(path); err != nil {
		return nil, err
	}
	db, err := sql.Open("sqlite3", path)
	if err != nil {
		return nil, err
	}
	defer db.Close()

	var data string
	row := db.QueryRow(`SELECT data FROM state_store WHERE id = ?`, "cluster")
	if err := row.Scan(&data); err != nil {
		if err == sql.ErrNoRows {
			// return empty state
			return state.NewClusterState(), nil
		}
		return nil, fmt.Errorf("read state: %w", err)
	}
	cs := state.NewClusterState()
	if err := cs.FromJSON([]byte(data)); err != nil {
		return nil, fmt.Errorf("unmarshal state: %w", err)
	}
	return cs, nil
}

// ControlLoopIteration performs a single reconcile+schedule iteration and persists state back to DB
func ControlLoopIteration(dbPath string) (*state.ClusterState, error) {
	cs, err := LoadState(dbPath)
	if err != nil {
		return nil, err
	}
	// reconcile
	controllers := stateControllers()
	if controllers != nil {
		controllers.ReconcileDeployments(cs)
	}
	// schedule pending pods
	sched := stateScheduler()
	if sched != nil {
		sched.SchedulePendingPods(cs)
	}
	// persist
	if err := SaveState(cs, dbPath); err != nil {
		return nil, err
	}
	return cs, nil
}

// ControlLoop runs continuously
func ControlLoop(dbPath string, intervalSeconds int) error {
	for {
		if _, err := ControlLoopIteration(dbPath); err != nil {
			return err
		}
		// sleep
		time.Sleep(time.Duration(intervalSeconds) * time.Second)
	}
}

// Helper indirections to avoid import cycles with controllers/scheduler
var stateControllers func() *controllersShim
var stateScheduler func() *schedulerShim

type controllersShim struct {
	ReconcileDeployments func(*state.ClusterState)
}

type schedulerShim struct {
	SchedulePendingPods func(*state.ClusterState)
}

// RegisterControllers allows main package to wire controllers implementation
func RegisterControllers(reconcile func(*state.ClusterState)) {
	stateControllers = func() *controllersShim {
		return &controllersShim{ReconcileDeployments: reconcile}
	}
}

// RegisterScheduler allows main package to wire scheduler implementation
func RegisterScheduler(schedule func(*state.ClusterState)) {
	stateScheduler = func() *schedulerShim {
		return &schedulerShim{SchedulePendingPods: schedule}
	}
}
