package main

import "fmt"

func main() {
	// fmt.Println("Hello ")

	// var name string = "Nemesis"

	// var name2 = "Violet"

	// name3 := "Mikasa"

	// fmt.Println(name)
	// fmt.Println(name2)
	// fmt.Println(name3)

	const MaxRetries = 3
	const (
		StatusRunning = "Running"
		StatusFailed  = "failed"
	)
	// kHoi tao chua co gia tri
	// 	var age int = 25
	// 	var price float64 = 19.99
	// 	var count uint = 100

	// 	var name string = "Hephaetus"

	// 	var isActive bool = true

	// 	var i int
	// 	var f float64
	// 	var s string
	// 	var b bool

	users := []string{"Alice", "Bob", "Charlie"}
	fmt.Println(users)
	var result []string
	result = append(result, "Data-1")
	result = append(result, "Data-2")
	result = append(result, "Data-3")
	fmt.Println(result)

	orders := make([]string, 0, 100)
	orders = append(orders, "Order-66")
	fmt.Println(orders)

	fmt.Println(len(orders))

}
