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

func updateAll(nums []int) []int {
	for i := range nums {
		nums[i] *= 2
	}
	return nums
}

func filterOddNumber(nums []int) []int {
	result := make([]int, 0, len(nums))

	for i := range nums {
		if nums[i]%2 != 0 {
			result = append(result, nums[i])
		}
	}

	return result
}

func findIndex(nums []int, target int) int {
	left := 0
	right := len(nums) - 1
	var mid int = 0
	for left <= right {
		mid = (left + right) / 2
		if target == nums[mid] {
			return mid
		} else if target > nums[mid] {
			left = mid + 1
		} else {
			right = mid - 1
		}

	}

	return -1
}

func removeDuplicates(nums []int) []int {
	seen := make(map[int]bool)
	result := []int{}

	for _, v := range nums {
		if !seen[v] {
			seen[v] = true
			result = append(result, v)
		}
	}
	return result
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

	// fmt.Println("-----------------")
	// fmt.Println("Delete at Index")
	// nums := []int{1, 2, 3, 4, 5}
	// index := 2
	// temp := append(nums[:index], nums[index+1:]...)
	// fmt.Println(temp)
	// fmt.Println("----------------")

	// nums := []int{1, 2, 4, 5}
	// index := 2
	// value := 3

	// temp := append(nums[:index], append([]int{value}, nums[index:]...)...)

	// fmt.Println(temp)

	// nums := []int{1, 2, 3}
	// fmt.Println(updateAll(nums))

	// nums := []int{1, 2, 3, 4, 5}
	// fmt.Println(filterOddNumber(nums))

	// nums := []int{10, 20, 30}
	// target := 20

	// fmt.Println(findIndex(nums, target))
	nums := []int{1, 2, 3, 3, 1}
	fmt.Println(removeDuplicates(nums))
}
