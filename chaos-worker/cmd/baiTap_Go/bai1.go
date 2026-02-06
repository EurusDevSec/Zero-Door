// Cấp độ 1: Làm nóng (Loop & Math)
// Bài 1: FizzBuzz (Kinh điển)
// In ra các số từ 1 đến n. Nếu chia hết cho 3 in "Fizz", chia hết cho 5 in "Buzz", chia hết cả 2 in "FizzBuzz".

// Input: n = 15

// Output: [1, 2, Fizz, 4, Buzz, Fizz, 7, 8, Fizz, Buzz, 11, Fizz, 13, 14, FizzBuzz]

// 💡 Best Practice: Dùng vòng lặp for cơ bản. Dùng if-else if-else. Nhớ là Go không cần ngoặc tròn () quanh điều kiện.

package main

import "fmt"

func main() {
	n := 15
	var result []string
	for i := 1; i <= n; i++ {
		if i%3 == 0 && i%5 == 0 {
			result = append(result, "FizzBuzz")
		} else if i%3 == 0 {
			result = append(result, "Fizz")

		} else if i%5 == 0 {
			result = append(result, "buzz")
		} else {
			result = append(result, fmt.Sprintf("%d", i))
		}

	}
	fmt.Println(result)

}
