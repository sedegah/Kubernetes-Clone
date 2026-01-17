package main

import (
	"fmt"
	"os"
	"strings"
	"text/tabwriter"

	"kclone-go/pkg/controllers"
	"kclone-go/pkg/lifecycle"
	"kclone-go/pkg/models"
	"kclone-go/pkg/resource"
	"kclone-go/pkg/scheduler"
	"kclone-go/pkg/service"

	"github.com/spf13/cobra"
)

func parseLabels(labelStr string) map[string]string {
	labels := make(map[string]string)
	if labelStr == "" {
		return labels
	}

	pairs := strings.Split(labelStr, ",")
	for _, pair := range pairs {
		parts := strings.SplitN(pair, "=", 2)
		if len(parts) == 2 {
			labels[strings.TrimSpace(parts[0])] = strings.TrimSpace(parts[1])
		}
	}
	return labels
}

func nodeAddCmd() *cobra.Command {
	var cpu, mem int
	var labels string

	cmd := &cobra.Command{
		Use:   "node-add [name]",
		Short: "Add a node to the cluster",
		Args:  cobra.ExactArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			name := args[0]
			node := &models.Node{
				Name:        name,
				CPUCapacity: cpu,
				MemCapacity: mem,
				Labels:      parseLabels(labels),
			}
			if err := clusterState.AddNode(node); err != nil {
				return err
			}
			fmt.Printf("Added node %s\n", name)
			scheduler.SchedulePendingPods(clusterState)
			return nil
		},
	}

	cmd.Flags().IntVar(&cpu, "cpu", 4, "CPU capacity")
	cmd.Flags().IntVar(&mem, "mem", 4096, "Memory capacity in MB")
	cmd.Flags().StringVar(&labels, "labels", "", "Comma-separated key=value labels")

	return cmd
}

func nodesCmd() *cobra.Command {
	return &cobra.Command{
		Use:   "nodes",
		Short: "List all nodes",
		RunE: func(cmd *cobra.Command, args []string) error {
			rows := resource.GetNodeResourceTable(clusterState)
			if len(rows) == 0 {
				fmt.Println("No nodes present")
				return nil
			}

			w := tabwriter.NewWriter(os.Stdout, 0, 0, 2, ' ', 0)
			fmt.Fprintln(w, "NAME\tCPU_USED\tCPU_CAPACITY\tMEM_USED\tMEM_CAPACITY")
			for _, row := range rows {
				fmt.Fprintf(w, "%s\t%d\t%d\t%d\t%d\n",
					row.Name, row.CPUUsed, row.CPUCapacity, row.MemUsed, row.MemCapacity)
			}
			w.Flush()
			return nil
		},
	}
}

func podCreateCmd() *cobra.Command {
	var image, labels string
	var cpu, mem int

	cmd := &cobra.Command{
		Use:   "pod-create [name]",
		Short: "Create a pod",
		Args:  cobra.ExactArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			name := args[0]
			spec := models.PodSpec{
				Name:       name,
				Image:      image,
				CPURequest: cpu,
				MemRequest: mem,
				Labels:     parseLabels(labels),
			}
			pod := lifecycle.CreatePod(clusterState, spec)
			fmt.Printf("Created pod %s -> %s\n", pod.UID, pod.Status.Phase)
			return nil
		},
	}

	cmd.Flags().StringVar(&image, "image", "", "Container image (required)")
	cmd.MarkFlagRequired("image")
	cmd.Flags().IntVar(&cpu, "cpu", 1, "CPU request")
	cmd.Flags().IntVar(&mem, "mem", 128, "Memory request in MB")
	cmd.Flags().StringVar(&labels, "labels", "", "Comma-separated key=value labels")

	return cmd
}

func podsCmd() *cobra.Command {
	return &cobra.Command{
		Use:   "pods",
		Short: "List all pods",
		RunE: func(cmd *cobra.Command, args []string) error {
			pods := clusterState.GetPods()
			if len(pods) == 0 {
				fmt.Println("No pods present")
				return nil
			}

			w := tabwriter.NewWriter(os.Stdout, 0, 0, 2, ' ', 0)
			fmt.Fprintln(w, "UID\tNAME\tIMAGE\tPHASE\tNODE\tCPU\tMEM")
			for _, pod := range pods {
				fmt.Fprintf(w, "%s\t%s\t%s\t%s\t%s\t%d\t%d\n",
					pod.UID, pod.Name, pod.Spec.Image, pod.Status.Phase,
					pod.Status.NodeName, pod.Spec.CPURequest, pod.Spec.MemRequest)
			}
			w.Flush()
			return nil
		},
	}
}

func podDeleteCmd() *cobra.Command {
	return &cobra.Command{
		Use:   "pod-delete [uid]",
		Short: "Delete a pod",
		Args:  cobra.ExactArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			uid := args[0]
			if err := lifecycle.DeletePod(clusterState, uid); err != nil {
				return err
			}
			fmt.Printf("Deleted pod %s\n", uid)
			return nil
		},
	}
}

func deployCreateCmd() *cobra.Command {
	var image, selector, labels string
	var replicas, cpu, mem int

	cmd := &cobra.Command{
		Use:   "deploy-create [name]",
		Short: "Create a deployment",
		Args:  cobra.ExactArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			name := args[0]

			sel := parseLabels(selector)
			if len(sel) == 0 {
				sel = map[string]string{"app": name}
			}

			lbls := parseLabels(labels)
			if len(lbls) == 0 {
				lbls = map[string]string{"app": name}
			}

			deploy := &models.Deployment{
				Name:       name,
				Image:      image,
				Replicas:   replicas,
				Selector:   sel,
				Labels:     lbls,
				CPURequest: cpu,
				MemRequest: mem,
			}

			if err := controllers.CreateDeployment(clusterState, deploy); err != nil {
				return err
			}
			controllers.ReconcileDeployments(clusterState)
			fmt.Printf("Created deployment %s with %d replicas\n", name, replicas)
			return nil
		},
	}

	cmd.Flags().StringVar(&image, "image", "", "Container image (required)")
	cmd.MarkFlagRequired("image")
	cmd.Flags().IntVar(&replicas, "replicas", 1, "Number of replicas")
	cmd.Flags().StringVar(&selector, "selector", "", "Selector labels (key=value,...)")
	cmd.Flags().StringVar(&labels, "labels", "", "Pod template labels (key=value,...)")
	cmd.Flags().IntVar(&cpu, "cpu", 1, "CPU request per pod")
	cmd.Flags().IntVar(&mem, "mem", 128, "Memory request per pod in MB")

	return cmd
}

func deployScaleCmd() *cobra.Command {
	var replicas int

	cmd := &cobra.Command{
		Use:   "deploy-scale [name]",
		Short: "Scale a deployment",
		Args:  cobra.ExactArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			name := args[0]
			deploy, exists := clusterState.GetDeployment(name)
			if !exists {
				return fmt.Errorf("deployment %s not found", name)
			}

			deploy.Replicas = replicas
			controllers.ReconcileDeployments(clusterState)
			fmt.Printf("Scaled %s to %d replicas\n", name, replicas)
			return nil
		},
	}

	cmd.Flags().IntVar(&replicas, "replicas", 1, "Number of replicas")
	cmd.MarkFlagRequired("replicas")

	return cmd
}

func serviceCreateCmd() *cobra.Command {
	var selector string
	var port, targetPort int

	cmd := &cobra.Command{
		Use:   "service-create [name]",
		Short: "Create a service",
		Args:  cobra.ExactArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			name := args[0]

			sel := parseLabels(selector)
			if len(sel) == 0 {
				sel = map[string]string{"app": name}
			}

			svc, err := service.CreateService(clusterState, name, sel, port, targetPort)
			if err != nil {
				return err
			}
			fmt.Printf("Created service %s with VIP %s\n", name, svc.VirtualIP)
			return nil
		},
	}

	cmd.Flags().StringVar(&selector, "selector", "", "Selector labels (key=value,...)")
	cmd.Flags().IntVar(&port, "port", 80, "Service port")
	cmd.Flags().IntVar(&targetPort, "target-port", 80, "Target port")

	return cmd
}

func servicesCmd() *cobra.Command {
	return &cobra.Command{
		Use:   "services",
		Short: "List all services",
		RunE: func(cmd *cobra.Command, args []string) error {
			services := clusterState.GetServices()
			if len(services) == 0 {
				fmt.Println("No services present")
				return nil
			}

			w := tabwriter.NewWriter(os.Stdout, 0, 0, 2, ' ', 0)
			fmt.Fprintln(w, "NAME\tVIP\tPORT\tTARGETS")
			for _, svc := range services {
				targets := strings.Join(svc.Endpoints, ",")
				fmt.Fprintf(w, "%s\t%s\t%d\t%s\n",
					svc.Name, svc.VirtualIP, svc.Port, targets)
			}
			w.Flush()
			return nil
		},
	}
}

func serviceRouteCmd() *cobra.Command {
	return &cobra.Command{
		Use:   "service-route [name]",
		Short: "Route a request through a service",
		Args:  cobra.ExactArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			name := args[0]
			podUID, err := service.RouteRequest(clusterState, name)
			if err != nil {
				return err
			}
			fmt.Printf("Service %s routed to pod %s\n", name, podUID)
			return nil
		},
	}
}

func statusCmd() *cobra.Command {
	return &cobra.Command{
		Use:   "status",
		Short: "Show cluster resource status",
		RunE: func(cmd *cobra.Command, args []string) error {
			caps := resource.GetClusterCapacity(clusterState)

			w := tabwriter.NewWriter(os.Stdout, 0, 0, 2, ' ', 0)
			fmt.Fprintln(w, "CPU_USED\tCPU_TOTAL\tMEM_USED\tMEM_TOTAL")
			fmt.Fprintf(w, "%d\t%d\t%d\t%d\n",
				caps.CPUUsed, caps.CPUTotal, caps.MemUsed, caps.MemTotal)
			w.Flush()
			return nil
		},
	}
}
