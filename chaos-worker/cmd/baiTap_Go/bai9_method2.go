package main

import "fmt"

func twoSum(nums []int, target int) []int {
	var complement int

	m := make(map[int]int)
	for i, v := range nums {
		complement = target - v
		if idx, ok := m[complement]; ok {
			return []int{idx, i}
		}
		m[v] = i
	}
	return nil
}

func main() {
	nums := []int{2, 7, 11, 15}

	target := 9
	result := twoSum(nums, target)
	fmt.Println(result)
}
