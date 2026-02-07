// Bài 6: Đảo ngược chuỗi (Reverse String)
// Cho một chuỗi, trả về chuỗi đảo ngược. (Gợi ý: Chuỗi trong Go có thể chuyển thành slice byte hoặc rune).

// Input: s = "golang"

// Output: "gnalog"

// 💡 Best Practice: Trong Go, chuỗi là bất biến (immutable). Bạn cần chuyển nó sang slice rune runes := []rune(s), đảo ngược slice đó, rồi ép kiểu lại về string.

package main

import (
	"fmt"
	"time"
)

func reverseString(s string) string {
	runes := []rune(s)
	for i, j := 0, len(runes)-1; i < j; i, j = i+1, j-1 {
		runes[i], runes[j] = runes[j], runes[i]
	}

	return string(runes)
}

func main() {
	input := "golang"
	start := time.Now()
	result := reverseString(input)
	fmt.Printf("go mat: %v\n", time.Since(start))
	fmt.Println(result)

}
