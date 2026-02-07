package main

import (
	"fmt"
)

func fibo(n int) []int {
	result := make([]int, 0)

	a := 0
	b := 1
	result = append(result, a)
	result = append(result, b)
	var c int
	for i := 2; i < n; i++ {
		c = a + b
		a = b
		b = c
		result = append(result, c)
	}

	return result
}
func main() {

	n := 6
	result := fibo(n)
	fmt.Println(result)

}
