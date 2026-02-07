package main

import (
	"fmt"
)

func initSlice() {
	nums := make([]int, 0, 5)

	fmt.Printf("len of nums %v, cap of nums %v \n", len(nums), cap(nums))
	nums = append(nums, 5)
	nums = append(nums, 10)
	fmt.Printf("len of nums %v, cap of nums %v\n", len(nums), cap(nums))

}

func cloneSlice(src []int) []int {
	dst := make([]int, len(src))
	copy(dst, src)
	return dst
}

func getSubSlice(arr []int) []int {
	return arr[1:4]

}

func mergeSlices(s1 []int, s2 []int) []int {

	s1 = append(s1, s2...)
	return s1
}

func main() {

	// fmt.Println("Bai1 - InitSlice")
	// initSlice()
	// fmt.Println("------------")
	// fmt.Println("Bai2 - clone Slice")
	// src := []int{1, 2, 3}
	// result := cloneSlice(src)
	// fmt.Println(result)
	// fmt.Println("------------")
	// fmt.Println("Bai 3 - GetSubSlice")
	// arr := []int{10, 20, 30, 40, 50}
	// fmt.Print(getSubSlice(arr))
	// fmt.Println("------------")

	// s1 := []int{1, 2}
	// s2 := []int{3, 4}
	// merge := mergeSlices(s1, s2)
	// fmt.Println(merge)

	// input := []int{1, 2, 3}
	// fmt.Println("-----------------")
	// fmt.Println(input[len(input)-1])

	fmt.Println("-----------------")
	fmt.Println("Delete at Index")
	nums := []int{1, 2, 3, 4, 5}
	index := 2
	temp := append(nums[:index], nums[index+1:]...)
	fmt.Println(temp)
}
