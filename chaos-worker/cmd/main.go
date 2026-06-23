package main

import (
	"fmt"
	"log"
	"os"
	"os/signal"
	"syscall"
)

func main() {
	log.Println("Starting Zero Door Chaos Worker...")

	// Listen for OS signals to stop gracefully
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	fmt.Println("Chaos Worker is running. Waiting for commands...")

	sig := <-sigChan
	log.Printf("Received signal: %v. Shutting down gracefully...\n", sig)
}
