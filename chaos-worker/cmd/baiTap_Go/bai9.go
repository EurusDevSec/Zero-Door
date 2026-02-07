// Bài 9: Two Sum (Bài toán phỏng vấn kinh điển)
// Cho một mảng nums và một số target. Tìm chỉ số (index) của 2 số sao cho tổng của chúng bằng target.

// Input: nums = [2, 7, 11, 15], target = 9

// Output: [0, 1] (Vì nums[0] + nums[1] = 2 + 7 = 9)

// 💡 Best Practice: Dùng Map để lưu trữ {giá_trị: chỉ_số}. Duyệt mảng một lần (O(n)). Sử dụng "comma ok" idiom để kiểm tra số còn thiếu có trong Map không.

package main

import "fmt"

func twoSum(nums []int, target int) []int {
	left := 0
	right := len(nums) - 1

	for left < right {
		currentSum := nums[left] + nums[right]
		if currentSum == target {
			return []int{left, right}

		} else if currentSum < target {
			left++

		} else {
			right--
		}
	}
	return nil
}

func main() {
	nums := []int{2, 7, 11, 15}
	target := 9
	result := twoSum(nums, target)
	fmt.Println(result)

}
