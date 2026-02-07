// Bài 3: Tổng các số chẵn (Sum Evens)
// Cho một Slice số nguyên. Tính tổng các số chẵn trong đó.

// Input: nums = [1, 2, 3, 4, 10, 11]

// Output: 16 (2 + 4 + 10)

// 💡 Best Practice: Dùng for _, v := range nums để duyệt mảng. Dùng toán tử % để kiểm tra chẵn lẻ.

package main

import "fmt"

func main() {

	nums := []int{1, 2, 3, 4, 10, 11}
	sum := 0
	for _, n := range nums { // _ la index, n la value
		if n%2 == 0 {
			sum += n
		}
	}
	fmt.Println(sum)
}
