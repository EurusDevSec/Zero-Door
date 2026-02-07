// Bài 5: Lọc phần tử (Filter Slice)
// Cho một Slice số nguyên, trả về một Slice mới chỉ chứa các số > 10.

// Input: nums = [5, 12, 8, 20, 1]

// Output: [12, 20]

// 💡 Best Practice:

// Tạo slice rỗng: var result []int (hoặc result := make([]int, 0)).

// Dùng append để thêm vào slice mới.

package main

import (
	"fmt"
)

func main() {

	nums := []int{5, 12, 8, 20, 1}
	result := []int{}

	for _, v := range nums {
		if v > 10 {
			result = append(result, v)

		}

	}
	fmt.Print(result)

}
