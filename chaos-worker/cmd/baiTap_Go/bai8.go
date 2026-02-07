// Bài 8: Đếm số lần xuất hiện (Word Count)
// Cho một Slice các chuỗi. Đếm xem mỗi chuỗi xuất hiện bao nhiêu lần.

// Input: words = ["apple", "banana", "apple", "orange", "banana", "apple"]

// Output: map[apple:3 banana:2 orange:1]

// 💡 Best Practice: Sử dụng Map. Key là từ, Value là số lần đếm.

// Khởi tạo: counts := make(map[string]int)

// Logic: counts[word]++

package main

// func wordCount()
import "fmt"

func main() {
	words := []string{"apple", "banana", "apple", "orange", "banana", "apple"}

	counts := make(map[string]int)
	for _, v := range words {
		counts[v]++
	}
	fmt.Println(counts)
}
