// Bài 4: Tìm số lớn nhất (Find Max)
// Tìm giá trị lớn nhất trong một Slice số nguyên.

// Input: nums = [10, 5, 8, 99, 2]

// Output: 99

// 💡 Best Practice: Giả định phần tử đầu tiên là Max. Dùng range để so sánh các phần tử còn lại.

package main

import "fmt"

func main() {
	nums := []int{10, 5, 8, 99, 2}

	max_nums := -9999

	for _, v := range nums {
		if v > max_nums {
			max_nums = v
		}
	}
	fmt.Println(max_nums)
}
