package persistence

import (
	"fmt"
	"os"

	"kclone-go/pkg/state"
)

// SaveState saves the cluster state to a JSON file
func SaveState(cs *state.ClusterState, path string) error {
	data := cs.ToJSON()
	if err := os.WriteFile(path, data, 0644); err != nil {
		return fmt.Errorf("write state: %w", err)
	}
	return nil
}

// LoadState loads cluster state from a JSON file
func LoadState(path string) (*state.ClusterState, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("read state: %w", err)
	}
	cs := state.NewClusterState()
	if err := cs.FromJSON(data); err != nil {
		return nil, fmt.Errorf("unmarshal state: %w", err)
	}
	return cs, nil
}
