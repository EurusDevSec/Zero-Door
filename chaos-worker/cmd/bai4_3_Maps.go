package main

import (
	"fmt"
)

func main() {

	// Khai bao va khoi tao
	podStatus := map[string]string{
		"pod-1": "running",
		"pod-2": "Pending",
	}

	fmt.Println(podStatus)
	status := "Running"
	if status == "Running" {
		fmt.Println("Pod is healthy")

	} else if status == "Pending" {
		fmt.Println("Pod is starting")
	} else {
		fmt.Println("Pod has issues")
	}

	action := "kill"
	switch action {
	case "kill":
		fmt.Println("killpod")

	case "stress":
		fmt.Println("StreeCPU")
	case "network":
		fmt.Println("injectLatency")
	default:
		fmt.Println("Unknown action")

	}
}
