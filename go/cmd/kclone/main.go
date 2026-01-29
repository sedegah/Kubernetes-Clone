package main

import (
	"fmt"
	"os"

	"kclone-go/pkg/controllers"
	"kclone-go/pkg/db"
	"kclone-go/pkg/scheduler"
	"kclone-go/pkg/state"

	"github.com/spf13/cobra"
)

var clusterState *state.ClusterState
var dbPath string

func init() {
	clusterState = state.NewClusterState()
}

func main() {
	rootCmd := &cobra.Command{
		Use:   "kclone",
		Short: "Simplified Kubernetes-style cluster manager",
		Long:  "A lightweight orchestrator with pod scheduling, services, and replica management",
	}
	// persistent DB flag (default to golang_cluster.db for Go CLI)
	rootCmd.PersistentFlags().StringVar(&dbPath, "db", "golang_cluster.db", "Path to SQLite DB to use as state store")

	// perform DB wiring and optional load after flags are parsed
	rootCmd.PersistentPreRun = func(cmd *cobra.Command, args []string) {
		if dbPath != "" {
			db.RegisterControllers(controllers.ReconcileDeployments)
			db.RegisterScheduler(scheduler.SchedulePendingPods)
			if cs, err := db.LoadState(dbPath); err == nil {
				clusterState = cs
			}
		}
	}
	rootCmd.AddCommand(
		nodeAddCmd(),
		nodesCmd(),
		nodeDeleteCmd(),
		podCreateCmd(),
		podsCmd(),
		podDeleteCmd(),
		deployCreateCmd(),
		deployScaleCmd(),
		serviceCreateCmd(),
		servicesCmd(),
		serviceRouteCmd(),
		statusCmd(),
		stateSaveCmd(),
		stateLoadCmd(),
	)

	if err := rootCmd.Execute(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
