// Bài 7: Xếp loại học sinh (Switch Case)
// Cho điểm số (0-100). Trả về xếp loại: >=90: "A", >=80: "B", >=70: "C", <70: "D".

// Input: score = 85

// Output: "B"

// 💡 Best Practice: Dùng Tagless Switch (Switch không có biểu thức) để code sạch hơn if-else.

package main

import (
	"fmt"
)

func rankingStudent(score int) (string, error) {
	if score < 0 || score > 100 {
		return "", fmt.Errorf("Diem so %d  khong hop le (phai tu 0-100)", score)
	}
	switch {
	case score >= 90:
		return "A", nil
	case score >= 80:
		return "B", nil
	case score >= 70:
		return "C", nil
	default:
		return "D", nil
	}
}

func main() {

	score := 85

	result, err := rankingStudent(score)

	if err != nil {
		fmt.Println("Loi: ", err)
		return
	}

	fmt.Println(result)

}
