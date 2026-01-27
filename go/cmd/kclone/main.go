package main

import (
	"fmt"
	"os"

	"kclone-go/pkg/state"

	"github.com/spf13/cobra"
)

var clusterState *state.ClusterState

func init() {
	clusterState = state.NewClusterState()
}

func main() {
	rootCmd := &cobra.Command{
		Use:   "kclone",
		Short: "Simplified Kubernetes-style cluster manager",
		Long:  "A lightweight orchestrator with pod scheduling, services, and replica management",
	}

	rootCmd.AddCommand(
		nodeAddCmd(),
		nodesCmd(),
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

