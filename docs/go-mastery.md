# 🚀 GO MASTERY - Từ Zero đến Production

> **Mục tiêu:** Nắm vững Go để xây dựng Chaos Engineering Tools cho Zero Door Project.
> **Thời gian học:** 2-3 tuần nếu học nghiêm túc.

---

## 📑 MỤC LỤC

1. [Tại sao Go cho Zero Door?](#1-tại-sao-go-cho-zero-door)
2. [Setup & Tooling](#2-setup--tooling)
3. [Cú pháp Cơ bản](#3-cú-pháp-cơ-bản)
4. [Kiểu Dữ liệu & Struct](#4-kiểu-dữ-liệu--struct)
5. [Control Flow](#5-control-flow)
6. [Functions & Methods](#6-functions--methods)
7. [Pointers](#7-pointers)
8. [Interfaces](#8-interfaces)
9. [Error Handling](#9-error-handling)
10. [Concurrency (Goroutines & Channels)](#10-concurrency-goroutines--channels)
11. [Packages & Modules](#11-packages--modules)
12. [Testing](#12-testing)
13. [HTTP & REST API](#13-http--rest-api)
14. [Kubernetes Client-Go](#14-kubernetes-client-go)
15. [CLI với Cobra](#15-cli-với-cobra)
16. [YAML/JSON & Configuration](#16-yamljson--configuration)
17. [Docker SDK](#17-docker-sdk)
18. [Prometheus & Metrics](#18-prometheus--metrics)
19. [Structured Logging](#19-structured-logging)
20. [File I/O & OS Operations](#20-file-io--os-operations)
21. [Best Practices & Patterns](#21-best-practices--patterns)
22. [Project Structure cho Zero Door](#22-project-structure-cho-zero-door)
23. [DevOps Roadmap 4 Tuần](#23-devops-roadmap-4-tuần)

---

## 1. Tại sao Go cho Zero Door?

| Lý do                      | Giải thích                                   |
| -------------------------- | -------------------------------------------- |
| **Kubernetes native**      | K8s, Docker, Prometheus đều viết bằng Go     |
| **Single binary**          | Build 1 file, copy vào container, chạy luôn  |
| **Concurrency**            | Goroutines xử lý hàng ngàn request đồng thời |
| **Performance**            | Nhanh gần C, nhưng code dễ như Python        |
| **Cloud-native ecosystem** | client-go, controller-runtime, Operator SDK  |

**Kết luận:** Go là ngôn ngữ "mẹ đẻ" của Cloud-Native. Viết Chaos tools bằng Go = đúng người đúng việc.

---

## 2. Setup & Tooling

### 2.1. Kiểm tra cài đặt

```bash
go version
# go version go1.22.0 windows/amd64
```

### 2.2. Cấu hình GOPATH (Optional - Go Modules đã thay thế)

```bash
# Không cần set GOPATH nữa nếu dùng Go Modules (Go 1.11+)
# Go tự động lưu packages vào ~/go/pkg/mod
```

### 2.3. Công cụ cần thiết

```bash
# Formatter (tự động format code)
go fmt ./...

# Linter (bắt lỗi code style)
go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
golangci-lint run

# Language Server (cho VS Code)
go install golang.org/x/tools/gopls@latest
```

### 2.4. VS Code Extensions

- **Go** (by Go Team at Google) - BẮT BUỘC
- **Error Lens** - Hiển thị lỗi inline

---

## 3. Cú pháp Cơ bản

### 3.1. Hello World

```go
package main

import "fmt"

func main() {
    fmt.Println("Zero Door - Chaos Engineering")
}
```

**Chạy:**

```bash
go run main.go
```

### 3.2. Khai báo biến

```go
// Cách 1: Khai báo đầy đủ
var name string = "Nemesis"

// Cách 2: Type inference (Go tự suy luận kiểu)
var name = "Nemesis"

// Cách 3: Short declaration (CHỈ DÙNG TRONG FUNCTION) ⭐ BEST
name := "Nemesis"

// Constants
const MaxRetries = 3
const (
    StatusRunning = "running"
    StatusFailed  = "failed"
)
```

### 3.3. In ra màn hình

```go
name := "Gaia"
count := 42

fmt.Println("Hello", name)                    // Hello Gaia
fmt.Printf("Agent: %s, Count: %d\n", name, count)  // Agent: Gaia, Count: 42
fmt.Sprintf("Agent: %s", name)                // Trả về string, không in

// Format specifiers quan trọng
// %s = string
// %d = integer
// %f = float
// %v = any value (tự detect)
// %+v = struct với field names
// %T = type của biến
```

---

## 4. Kiểu Dữ liệu & Struct

### 4.1. Basic Types

```go
// Numbers
var age int = 25           // int, int8, int16, int32, int64
var price float64 = 19.99  // float32, float64
var count uint = 100       // unsigned (không âm)

// String
var name string = "Hephaestus"

// Boolean
var isActive bool = true

// Zero values (giá trị mặc định)
var i int      // 0
var f float64  // 0.0
var s string   // ""
var b bool     // false
```

### 4.2. Arrays & Slices

```go

// Slice: Kích thước ĐỘNG (dùng nhiều) ⭐
pods := []string{"pod-1", "pod-2", "pod-3"}

// Tạo slice rỗng
var emptySlice []int           // nil slice
emptySlice := make([]int, 0)   // empty slice (preferred)

// Thêm phần tử
pods = append(pods, "pod-4")

// Slice của slice
firstTwo := pods[0:2]  // ["pod-1", "pod-2"]
fromSecond := pods[1:] // ["pod-2", "pod-3", "pod-4"]

// Độ dài
len(pods)  // 4

// Array: Kích thước CỐ ĐỊNH (ít dùng)
var arr [3]int = [3]int{1, 2, 3}

// Slice: Kích thước ĐỘNG (dùng nhiều) ⭐
pods := []string{"pod-1", "pod-2", "pod-3"}

// Tạo slice rỗng
var emptySlice []int           // nil slice
emptySlice := make([]int, 0)   // empty slice (preferred)

// Thêm phần tử
pods = append(pods, "pod-4")

// Slice của slice
firstTwo := pods[0:2]  // ["pod-1", "pod-2"]
fromSecond := pods[1:] // ["pod-2", "pod-3", "pod-4"]

// Độ dài
len(pods)  // 4


```

### 4.3. Maps

```go
// Khai báo và khởi tạo
podStatus := map[string]string{
    "pod-1": "Running",
    "pod-2": "Pending",
}

// Tạo map rỗng
m := make(map[string]int)

// CRUD
podStatus["pod-3"] = "Failed"       // Create/Update
status := podStatus["pod-1"]        // Read
delete(podStatus, "pod-2")          // Delete

// Kiểm tra key tồn tại (QUAN TRỌNG)
status, exists := podStatus["pod-99"]
if exists {
    fmt.Println(status)
} else {
    fmt.Println("Pod not found")
}
```

### 4.4. Struct ⭐ (Cực kỳ quan trọng)

```go
// Định nghĩa struct
type Pod struct {
    Name      string
    Namespace string
    Status    string
    Replicas  int
}

// Khởi tạo
pod := Pod{
    Name:      "nginx-abc123",
    Namespace: "default",
    Status:    "Running",
    Replicas:  3,
}

// Truy cập field
fmt.Println(pod.Name)

// Struct lồng nhau
type ChaosExperiment struct {
    ID        string
    Target    Pod       // Nested struct
    CreatedAt time.Time
}

// Anonymous struct (dùng nhanh, không cần định nghĩa trước)
config := struct {
    Timeout int
    Retries int
}{
    Timeout: 30,
    Retries: 3,
}
```

### 4.5. Struct Tags (cho JSON, YAML)

```go
type Attack struct {
    ID        string `json:"id" yaml:"id"`
    Type      string `json:"type" yaml:"type"`
    Duration  int    `json:"duration_seconds" yaml:"durationSeconds"`
    IsActive  bool   `json:"is_active,omitempty"` // omitempty: bỏ qua nếu false/empty
}

// Marshal (Go → JSON)
attack := Attack{ID: "atk-001", Type: "cpu-stress", Duration: 60}
jsonBytes, _ := json.Marshal(attack)
// {"id":"atk-001","type":"cpu-stress","duration_seconds":60}

// Unmarshal (JSON → Go)
var parsed Attack
json.Unmarshal(jsonBytes, &parsed)
```

---

## 5. Control Flow

### 5.1. If-Else

```go
status := "Running"

if status == "Running" {
    fmt.Println("Pod is healthy")
} else if status == "Pending" {
    fmt.Println("Pod is starting")
} else {
    fmt.Println("Pod has issues")
}

// If với statement khởi tạo (Go idiom) ⭐
if err := doSomething(); err != nil {
    fmt.Println("Error:", err)
}

// Kiểm tra map key
if val, ok := myMap[key]; ok {
    fmt.Println(val)
}
```

### 5.2. Switch

```go
action := "kill"

switch action {
case "kill":
    killPod()
case "stress":
    stressCPU()
case "network":
    injectLatency()
default:
    fmt.Println("Unknown action")
}

// Switch không cần expression
hour := time.Now().Hour()
switch {
case hour < 12:
    fmt.Println("Morning")
case hour < 18:
    fmt.Println("Afternoon")
default:
    fmt.Println("Evening")
}

// Type switch (cho interface{})
func describe(i interface{}) {
    switch v := i.(type) {
    case int:
        fmt.Println("Integer:", v)
    case string:
        fmt.Println("String:", v)
    default:
        fmt.Println("Unknown type")
    }
}
```

### 5.3. For Loop (Go chỉ có FOR, không có while)

```go
// Classic for
for i := 0; i < 5; i++ {
    fmt.Println(i)
}

// While-style
count := 0
for count < 5 {
    count++
}

// Infinite loop
for {
    // Dùng break để thoát
    if condition {
        break
    }
}

// Range (iterate slice/map/string) ⭐
pods := []string{"pod-1", "pod-2", "pod-3"}

for index, pod := range pods {
    fmt.Printf("%d: %s\n", index, pod)
}

// Bỏ qua index
for _, pod := range pods {
    fmt.Println(pod)
}

// Range với map
for key, value := range myMap {
    fmt.Printf("%s = %s\n", key, value)
}
```

---

## 6. Functions & Methods

### 6.1. Functions

```go
// Basic function
func sayHello(name string) {
    fmt.Println("Hello", name)
}

// Với return value
func add(a, b int) int {
    return a + b
}

// Multiple return values ⭐ (Go signature)
func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, errors.New("division by zero")
    }
    return a / b, nil
}

result, err := divide(10, 2)
if err != nil {
    log.Fatal(err)
}

// Named return values
func getConfig() (host string, port int) {
    host = "localhost"
    port = 8080
    return // naked return
}

// Variadic function (số lượng params không cố định)
func sum(nums ...int) int {
    total := 0
    for _, n := range nums {
        total += n
    }
    return total
}
sum(1, 2, 3, 4, 5) // 15
```

### 6.2. Methods (Function gắn với Struct)

```go
type Agent struct {
    Name   string
    Status string
}

// Method với value receiver
func (a Agent) Describe() string {
    return fmt.Sprintf("Agent %s is %s", a.Name, a.Status)
}

// Method với pointer receiver (có thể modify struct) ⭐
func (a *Agent) Activate() {
    a.Status = "active"
}

agent := Agent{Name: "Nemesis", Status: "idle"}
agent.Activate()
fmt.Println(agent.Describe()) // Agent Nemesis is active
```

**Quy tắc chọn receiver:**

- Dùng **pointer receiver** (`*T`) khi:
  - Cần modify struct
  - Struct lớn (tránh copy)
- Dùng **value receiver** (`T`) khi:
  - Chỉ đọc, không modify
  - Struct nhỏ (int, string, small struct)

### 6.3. Anonymous Functions & Closures

```go
// Anonymous function
func() {
    fmt.Println("I'm anonymous")
}()

// Gán vào biến
greet := func(name string) {
    fmt.Println("Hello", name)
}
greet("World")

// Closure (function giữ reference đến biến bên ngoài)
func counter() func() int {
    count := 0
    return func() int {
        count++
        return count
    }
}

c := counter()
fmt.Println(c()) // 1
fmt.Println(c()) // 2
fmt.Println(c()) // 3
```

---

## 7. Pointers

### 7.1. Cơ bản

```go
x := 10
p := &x  // p là pointer trỏ đến x

fmt.Println(p)   // 0xc000014088 (địa chỉ memory)
fmt.Println(*p)  // 10 (giá trị tại địa chỉ đó)

*p = 20          // Thay đổi giá trị thông qua pointer
fmt.Println(x)   // 20
```

### 7.2. Pointer với Struct

```go
type Config struct {
    Timeout int
}

// Không dùng pointer: COPY giá trị
func updateTimeout(c Config) {
    c.Timeout = 60  // Chỉ thay đổi bản copy
}

// Dùng pointer: Thay đổi ORIGINAL
func updateTimeoutPtr(c *Config) {
    c.Timeout = 60  // Thay đổi giá trị gốc
}

cfg := Config{Timeout: 30}
updateTimeout(cfg)
fmt.Println(cfg.Timeout)  // 30 (không đổi)

updateTimeoutPtr(&cfg)
fmt.Println(cfg.Timeout)  // 60 (đã đổi)
```

### 7.3. Khi nào dùng Pointer?

| Dùng Pointer                               | Dùng Value            |
| ------------------------------------------ | --------------------- |
| Cần modify giá trị gốc                     | Chỉ đọc, không modify |
| Struct lớn (tránh copy)                    | Struct nhỏ            |
| Slice, Map, Channel (đã là reference type) | Basic types nhỏ       |

---

## 8. Interfaces ⭐⭐⭐ (Quan trọng nhất của Go)

### 8.1. Định nghĩa Interface

```go
// Interface định nghĩa CONTRACT (hợp đồng)
type Attacker interface {
    Attack() error
    GetName() string
}

// Struct implement interface (NGẦM ĐỊNH, không cần khai báo)
type CPUStress struct {
    Intensity int
}

func (c CPUStress) Attack() error {
    fmt.Printf("Stressing CPU at %d%%\n", c.Intensity)
    return nil
}

func (c CPUStress) GetName() string {
    return "cpu-stress"
}

type PodKiller struct {
    TargetPod string
}

func (p PodKiller) Attack() error {
    fmt.Printf("Killing pod %s\n", p.TargetPod)
    return nil
}

func (p PodKiller) GetName() string {
    return "pod-kill"
}
```

### 8.2. Sử dụng Interface

```go
// Function nhận interface type
func executeAttack(a Attacker) {
    fmt.Println("Executing:", a.GetName())
    a.Attack()
}

// Có thể truyền bất kỳ type nào implement Attacker
executeAttack(CPUStress{Intensity: 80})
executeAttack(PodKiller{TargetPod: "nginx-123"})

// Slice of interfaces
attacks := []Attacker{
    CPUStress{Intensity: 50},
    PodKiller{TargetPod: "api-server"},
}

for _, attack := range attacks {
    attack.Attack()
}
```

### 8.3. Empty Interface `interface{}`

```go
// interface{} có thể chứa BẤT KỲ giá trị nào (như Object trong Java)
var anything interface{}

anything = 42
anything = "hello"
anything = CPUStress{Intensity: 100}

// Type assertion (lấy giá trị cụ thể từ interface{})
str, ok := anything.(string)
if ok {
    fmt.Println(str)
}

// Go 1.18+ dùng `any` thay cho `interface{}`
var anything any = "hello"
```

### 8.4. Common Interfaces trong Go

```go
// io.Reader - Đọc data
type Reader interface {
    Read(p []byte) (n int, err error)
}

// io.Writer - Ghi data
type Writer interface {
    Write(p []byte) (n int, err error)
}

// error - Mọi error trong Go
type error interface {
    Error() string
}

// fmt.Stringer - Custom string representation
type Stringer interface {
    String() string
}

// Implement Stringer
func (a Agent) String() string {
    return fmt.Sprintf("Agent<%s>", a.Name)
}
```

---

## 9. Error Handling ⭐⭐

Go không có try-catch. Mọi error được return explicitly.

### 9.1. Cơ bản

```go
// Kiểm tra error (pattern phổ biến nhất)
result, err := someFunction()
if err != nil {
    return err  // hoặc xử lý error
}
// Tiếp tục dùng result

// ❌ SAI: Bỏ qua error
result, _ := someFunction()  // KHÔNG BAO GIỜ làm vậy với real code
```

### 9.2. Tạo Error

```go
import "errors"

// Cách 1: errors.New()
func divide(a, b int) (int, error) {
    if b == 0 {
        return 0, errors.New("cannot divide by zero")
    }
    return a / b, nil
}

// Cách 2: fmt.Errorf() - với formatting
func getUser(id int) (*User, error) {
    if id <= 0 {
        return nil, fmt.Errorf("invalid user id: %d", id)
    }
    // ...
}
```

### 9.3. Custom Error Types

```go
type AttackError struct {
    Target  string
    Reason  string
}

func (e *AttackError) Error() string {
    return fmt.Sprintf("attack on %s failed: %s", e.Target, e.Reason)
}

func attack(target string) error {
    // ...
    return &AttackError{
        Target: target,
        Reason: "pod not found",
    }
}

// Type assertion để lấy thông tin chi tiết
err := attack("nginx")
if attackErr, ok := err.(*AttackError); ok {
    fmt.Println("Failed target:", attackErr.Target)
}
```

### 9.4. Error Wrapping (Go 1.13+)

```go
// Wrap error với context
func processConfig(path string) error {
    data, err := os.ReadFile(path)
    if err != nil {
        return fmt.Errorf("failed to read config: %w", err)
    }
    // ...
}

// Unwrap để kiểm tra root cause
if errors.Is(err, os.ErrNotExist) {
    fmt.Println("File not found")
}

// Lấy error type cụ thể
var pathErr *os.PathError
if errors.As(err, &pathErr) {
    fmt.Println("Path:", pathErr.Path)
}
```

### 9.5. Panic & Recover (Dùng hạn chế)

```go
// panic: Crash chương trình (chỉ dùng khi THỰC SỰ critical)
func mustParseConfig() Config {
    cfg, err := parseConfig()
    if err != nil {
        panic("config is required: " + err.Error())
    }
    return cfg
}

// recover: Bắt panic (thường dùng trong middleware)
func safeExecute(fn func()) {
    defer func() {
        if r := recover(); r != nil {
            fmt.Println("Recovered from:", r)
        }
    }()
    fn()
}
```

---

## 10. Concurrency (Goroutines & Channels) ⭐⭐⭐

**Đây là sức mạnh lớn nhất của Go.**

### 10.1. Goroutines

```go
// Goroutine = lightweight thread (chỉ ~2KB memory)
func sayHello(name string) {
    fmt.Println("Hello", name)
}

// Chạy function trong goroutine mới
go sayHello("World")

// Anonymous goroutine
go func() {
    fmt.Println("I'm running in a goroutine")
}()

// QUAN TRỌNG: main() không đợi goroutines
func main() {
    go sayHello("World")
    // Chương trình kết thúc ngay, không in gì cả!
}

// Cách đợi: dùng sync.WaitGroup
func main() {
    var wg sync.WaitGroup

    wg.Add(1)  // Đếm 1 goroutine
    go func() {
        defer wg.Done()  // Trừ 1 khi xong
        sayHello("World")
    }()

    wg.Wait()  // Đợi tất cả goroutines hoàn thành
}
```

### 10.2. Channels

```go
// Channel = ống dẫn để goroutines giao tiếp

// Tạo channel
ch := make(chan string)

// Gửi data vào channel (blocking)
ch <- "hello"

// Nhận data từ channel (blocking)
msg := <-ch

// Ví dụ: Goroutine gửi, main nhận
func main() {
    ch := make(chan string)

    go func() {
        ch <- "Hello from goroutine"
    }()

    msg := <-ch  // Đợi và nhận message
    fmt.Println(msg)
}
```

### 10.3. Buffered Channels

```go
// Unbuffered: Sender block cho đến khi có receiver
ch := make(chan int)

// Buffered: Sender không block nếu buffer còn chỗ
ch := make(chan int, 3)  // Buffer size = 3

ch <- 1  // Không block
ch <- 2  // Không block
ch <- 3  // Không block
ch <- 4  // BLOCK vì buffer đầy
```

### 10.4. Channel Patterns

```go
// Pattern 1: Worker Pool
func worker(id int, jobs <-chan int, results chan<- int) {
    for job := range jobs {
        results <- job * 2
    }
}

func main() {
    jobs := make(chan int, 100)
    results := make(chan int, 100)

    // Spawn 3 workers
    for w := 1; w <= 3; w++ {
        go worker(w, jobs, results)
    }

    // Send jobs
    for j := 1; j <= 9; j++ {
        jobs <- j
    }
    close(jobs)

    // Collect results
    for a := 1; a <= 9; a++ {
        <-results
    }
}
```

### 10.5. Select (Multiplexing channels)

```go
// Select = switch cho channels
select {
case msg := <-ch1:
    fmt.Println("Received from ch1:", msg)
case msg := <-ch2:
    fmt.Println("Received from ch2:", msg)
case ch3 <- "hello":
    fmt.Println("Sent to ch3")
default:
    fmt.Println("No channel ready")
}

// Timeout pattern
select {
case result := <-ch:
    fmt.Println(result)
case <-time.After(5 * time.Second):
    fmt.Println("Timeout!")
}
```

### 10.6. Context (Cancellation & Timeout)

```go
import "context"

// Context dùng để cancel goroutines, pass deadlines, values

func fetchData(ctx context.Context) error {
    select {
    case <-time.After(10 * time.Second):
        return nil  // Completed
    case <-ctx.Done():
        return ctx.Err()  // Cancelled hoặc timeout
    }
}

func main() {
    // Context với timeout
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()  // QUAN TRỌNG: luôn gọi cancel()

    err := fetchData(ctx)
    if err != nil {
        fmt.Println("Error:", err)
    }
}
```

### 10.7. Ví dụ thực tế: Parallel Pod Killer

```go
func killPodsParallel(pods []string) error {
    var wg sync.WaitGroup
    errCh := make(chan error, len(pods))

    for _, pod := range pods {
        wg.Add(1)
        go func(podName string) {
            defer wg.Done()
            if err := killPod(podName); err != nil {
                errCh <- fmt.Errorf("failed to kill %s: %w", podName, err)
            }
        }(pod)  // Truyền pod vào closure (quan trọng!)
    }

    wg.Wait()
    close(errCh)

    // Collect errors
    var errs []error
    for err := range errCh {
        errs = append(errs, err)
    }

    if len(errs) > 0 {
        return errors.Join(errs...)
    }
    return nil
}
```

---

## 11. Packages & Modules

### 11.1. Tạo Go Module

```bash
# Trong thư mục project
go mod init github.com/yourusername/zero-door

# Tạo ra file go.mod
```

### 11.2. Cấu trúc Package

```
zero-door/
├── go.mod
├── go.sum
├── cmd/
│   └── main.go           # package main
├── internal/             # Private packages (không export ra ngoài)
│   ├── attacker/
│   │   └── attacker.go   # package attacker
│   └── detector/
│       └── detector.go   # package detector
└── pkg/                  # Public packages (có thể import từ ngoài)
    └── types/
        └── types.go      # package types
```

### 11.3. Import & Export

```go
// ===== internal/attacker/attacker.go =====
package attacker

// TÊN VIẾT HOA = Exported (public)
type Attacker struct {
    Name string
}

// Tên viết thường = unexported (private)
type config struct {
    timeout int
}

// Exported function
func NewAttacker(name string) *Attacker {
    return &Attacker{Name: name}
}

// ===== cmd/main.go =====
package main

import (
    "fmt"
    "github.com/yourusername/zero-door/internal/attacker"
)

func main() {
    a := attacker.NewAttacker("Nemesis")
    fmt.Println(a.Name)
}
```

### 11.4. Quản lý Dependencies

```bash
# Thêm dependency
go get github.com/gin-gonic/gin

# Thêm với version cụ thể
go get github.com/gin-gonic/gin@v1.9.0

# Update tất cả dependencies
go get -u ./...

# Dọn dẹp unused dependencies
go mod tidy

# Download dependencies
go mod download
```

---

## 12. Testing

### 12.1. Unit Test cơ bản

```go
// ===== math.go =====
package math

func Add(a, b int) int {
    return a + b
}

// ===== math_test.go =====
package math

import "testing"

func TestAdd(t *testing.T) {
    result := Add(2, 3)
    expected := 5

    if result != expected {
        t.Errorf("Add(2, 3) = %d; want %d", result, expected)
    }
}
```

### 12.2. Table-Driven Tests ⭐

```go
func TestAdd(t *testing.T) {
    tests := []struct {
        name     string
        a, b     int
        expected int
    }{
        {"positive numbers", 2, 3, 5},
        {"negative numbers", -1, -2, -3},
        {"zero", 0, 0, 0},
        {"mixed", -1, 5, 4},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result := Add(tt.a, tt.b)
            if result != tt.expected {
                t.Errorf("Add(%d, %d) = %d; want %d",
                    tt.a, tt.b, result, tt.expected)
            }
        })
    }
}
```

### 12.3. Chạy Tests

```bash
# Chạy tất cả tests
go test ./...

# Với verbose output
go test -v ./...

# Chạy test cụ thể
go test -run TestAdd ./...

# Coverage
go test -cover ./...
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out  # Mở browser
```

### 12.4. Mocking với Interfaces

```go
// ===== service.go =====
type PodKiller interface {
    Kill(name string) error
}

type Service struct {
    killer PodKiller
}

func (s *Service) ExecuteAttack(pod string) error {
    return s.killer.Kill(pod)
}

// ===== service_test.go =====
type MockKiller struct {
    KilledPods []string
    Err        error
}

func (m *MockKiller) Kill(name string) error {
    m.KilledPods = append(m.KilledPods, name)
    return m.Err
}

func TestExecuteAttack(t *testing.T) {
    mock := &MockKiller{}
    svc := &Service{killer: mock}

    err := svc.ExecuteAttack("nginx-123")

    if err != nil {
        t.Fatal(err)
    }
    if len(mock.KilledPods) != 1 || mock.KilledPods[0] != "nginx-123" {
        t.Error("Expected pod to be killed")
    }
}
```

---

## 13. HTTP & REST API

### 13.1. HTTP Server với net/http (Standard Library)

```go
package main

import (
    "encoding/json"
    "net/http"
)

type HealthResponse struct {
    Status string `json:"status"`
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(HealthResponse{Status: "ok"})
}

func main() {
    http.HandleFunc("/health", healthHandler)
    http.ListenAndServe(":8080", nil)
}
```

### 13.2. HTTP Server với Gin (Recommended) ⭐

```go
package main

import (
    "net/http"
    "github.com/gin-gonic/gin"
)

type Attack struct {
    Type      string `json:"type" binding:"required"`
    TargetPod string `json:"target_pod" binding:"required"`
    Duration  int    `json:"duration"`
}

func main() {
    r := gin.Default()

    // Health check
    r.GET("/health", func(c *gin.Context) {
        c.JSON(http.StatusOK, gin.H{"status": "ok"})
    })

    // Get attacks
    r.GET("/attacks", func(c *gin.Context) {
        attacks := []Attack{
            {Type: "cpu-stress", TargetPod: "nginx", Duration: 60},
        }
        c.JSON(http.StatusOK, attacks)
    })

    // Create attack
    r.POST("/attacks", func(c *gin.Context) {
        var attack Attack
        if err := c.ShouldBindJSON(&attack); err != nil {
            c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
            return
        }
        // Process attack...
        c.JSON(http.StatusCreated, attack)
    })

    // Path parameter
    r.DELETE("/attacks/:id", func(c *gin.Context) {
        id := c.Param("id")
        c.JSON(http.StatusOK, gin.H{"deleted": id})
    })

    r.Run(":8080")
}
```

### 13.3. HTTP Client

```go
import (
    "net/http"
    "time"
    "io"
)

// Tạo client với timeout
client := &http.Client{
    Timeout: 10 * time.Second,
}

// GET request
resp, err := client.Get("https://api.example.com/pods")
if err != nil {
    log.Fatal(err)
}
defer resp.Body.Close()

body, _ := io.ReadAll(resp.Body)
fmt.Println(string(body))

// POST request với JSON
payload := map[string]string{"name": "test"}
jsonData, _ := json.Marshal(payload)

resp, err := client.Post(
    "https://api.example.com/pods",
    "application/json",
    bytes.NewBuffer(jsonData),
)
```

---

## 14. Kubernetes Client-Go ⭐⭐

**Đây là phần QUAN TRỌNG NHẤT cho Zero Door.**

### 14.1. Cài đặt

```bash
go get k8s.io/client-go@latest
go get k8s.io/apimachinery@latest
```

### 14.2. Kết nối tới Cluster

```go
package main

import (
    "context"
    "fmt"
    "path/filepath"

    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
    "k8s.io/client-go/kubernetes"
    "k8s.io/client-go/tools/clientcmd"
    "k8s.io/client-go/util/homedir"
)

func main() {
    // Load kubeconfig
    kubeconfig := filepath.Join(homedir.HomeDir(), ".kube", "config")
    config, err := clientcmd.BuildConfigFromFlags("", kubeconfig)
    if err != nil {
        panic(err)
    }

    // Tạo clientset
    clientset, err := kubernetes.NewForConfig(config)
    if err != nil {
        panic(err)
    }

    // List pods
    pods, err := clientset.CoreV1().Pods("default").List(
        context.TODO(),
        metav1.ListOptions{},
    )
    if err != nil {
        panic(err)
    }

    for _, pod := range pods.Items {
        fmt.Printf("Pod: %s, Status: %s\n", pod.Name, pod.Status.Phase)
    }
}
```

### 14.3. CRUD Operations trên Pods

```go
import (
    corev1 "k8s.io/api/core/v1"
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

ctx := context.Background()

// GET pod
pod, err := clientset.CoreV1().Pods("default").Get(ctx, "nginx", metav1.GetOptions{})

// LIST pods với label selector
pods, err := clientset.CoreV1().Pods("default").List(ctx, metav1.ListOptions{
    LabelSelector: "app=nginx",
})

// DELETE pod (CHAOS!)
err = clientset.CoreV1().Pods("default").Delete(ctx, "nginx-abc123", metav1.DeleteOptions{})

// CREATE pod
newPod := &corev1.Pod{
    ObjectMeta: metav1.ObjectMeta{
        Name: "test-pod",
    },
    Spec: corev1.PodSpec{
        Containers: []corev1.Container{
            {
                Name:  "nginx",
                Image: "nginx:latest",
            },
        },
    },
}
createdPod, err := clientset.CoreV1().Pods("default").Create(ctx, newPod, metav1.CreateOptions{})
```

### 14.4. Scale Deployment

```go
import (
    autoscalingv1 "k8s.io/api/autoscaling/v1"
)

// Lấy scale hiện tại
scale, err := clientset.AppsV1().Deployments("default").GetScale(
    ctx, "nginx-deployment", metav1.GetOptions{},
)

// Thay đổi replicas
scale.Spec.Replicas = 5
_, err = clientset.AppsV1().Deployments("default").UpdateScale(
    ctx, "nginx-deployment", scale, metav1.UpdateOptions{},
)
```

### 14.5. Watch Events (Real-time monitoring)

```go
// Watch pods trong namespace
watcher, err := clientset.CoreV1().Pods("default").Watch(ctx, metav1.ListOptions{})
if err != nil {
    panic(err)
}

for event := range watcher.ResultChan() {
    pod := event.Object.(*corev1.Pod)
    fmt.Printf("Event: %s, Pod: %s, Status: %s\n",
        event.Type, pod.Name, pod.Status.Phase)
}
```

### 14.6. Ví dụ: Pod Killer Agent (Nemesis)

```go
package main

import (
    "context"
    "fmt"
    "math/rand"
    "time"

    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
    "k8s.io/client-go/kubernetes"
    "k8s.io/client-go/tools/clientcmd"
)

type PodKiller struct {
    clientset *kubernetes.Clientset
    namespace string
}

func NewPodKiller(kubeconfig, namespace string) (*PodKiller, error) {
    config, err := clientcmd.BuildConfigFromFlags("", kubeconfig)
    if err != nil {
        return nil, err
    }

    clientset, err := kubernetes.NewForConfig(config)
    if err != nil {
        return nil, err
    }

    return &PodKiller{
        clientset: clientset,
        namespace: namespace,
    }, nil
}

func (pk *PodKiller) KillRandomPod(ctx context.Context, labelSelector string) error {
    // List pods matching selector
    pods, err := pk.clientset.CoreV1().Pods(pk.namespace).List(ctx, metav1.ListOptions{
        LabelSelector: labelSelector,
    })
    if err != nil {
        return fmt.Errorf("failed to list pods: %w", err)
    }

    if len(pods.Items) == 0 {
        return fmt.Errorf("no pods found with selector: %s", labelSelector)
    }

    // Pick random pod
    rand.Seed(time.Now().UnixNano())
    victim := pods.Items[rand.Intn(len(pods.Items))]

    // Kill it!
    fmt.Printf("🔪 Killing pod: %s\n", victim.Name)
    err = pk.clientset.CoreV1().Pods(pk.namespace).Delete(
        ctx, victim.Name, metav1.DeleteOptions{},
    )
    if err != nil {
        return fmt.Errorf("failed to kill pod: %w", err)
    }

    fmt.Printf("💀 Pod %s has been terminated\n", victim.Name)
    return nil
}

func main() {
    killer, err := NewPodKiller("~/.kube/config", "default")
    if err != nil {
        panic(err)
    }

    ctx := context.Background()
    err = killer.KillRandomPod(ctx, "app=nginx")
    if err != nil {
        fmt.Println("Error:", err)
    }
}
```

---

## 15. CLI với Cobra ⭐⭐⭐ (DevOps Essential)

**Cobra** là thư viện #1 để viết CLI tools. Kubernetes, Docker, Helm, Hugo đều dùng Cobra.

### 15.1. Cài đặt

```bash
go get github.com/spf13/cobra/cobra@latest
```

### 15.2. Cấu trúc CLI cơ bản

```go
// cmd/root.go
package cmd

import (
    "fmt"
    "os"
    "github.com/spf13/cobra"
)

var rootCmd = &cobra.Command{
    Use:   "zerodoor",
    Short: "Zero Door - Chaos Engineering CLI",
    Long:  `A CLI tool for managing chaos experiments in Kubernetes clusters.`,
}

func Execute() {
    if err := rootCmd.Execute(); err != nil {
        fmt.Fprintln(os.Stderr, err)
        os.Exit(1)
    }
}

func init() {
    // Global flags
    rootCmd.PersistentFlags().StringP("config", "c", "", "config file path")
    rootCmd.PersistentFlags().BoolP("verbose", "v", false, "verbose output")
}
```

### 15.3. Thêm Subcommands

```go
// cmd/attack.go
package cmd

import (
    "fmt"
    "github.com/spf13/cobra"
)

var (
    targetPod   string
    namespace   string
    attackType  string
    duration    int
)

var attackCmd = &cobra.Command{
    Use:   "attack",
    Short: "Execute chaos attack",
    Long:  `Execute various types of chaos attacks on Kubernetes resources.`,
    Run: func(cmd *cobra.Command, args []string) {
        fmt.Printf("Attacking pod %s in namespace %s\n", targetPod, namespace)
        fmt.Printf("Attack type: %s, Duration: %ds\n", attackType, duration)
    },
}

func init() {
    rootCmd.AddCommand(attackCmd)

    // Local flags cho command này
    attackCmd.Flags().StringVarP(&targetPod, "pod", "p", "", "target pod name (required)")
    attackCmd.Flags().StringVarP(&namespace, "namespace", "n", "default", "kubernetes namespace")
    attackCmd.Flags().StringVarP(&attackType, "type", "t", "kill", "attack type: kill, cpu, network")
    attackCmd.Flags().IntVarP(&duration, "duration", "d", 60, "attack duration in seconds")

    // Mark required flags
    attackCmd.MarkFlagRequired("pod")
}
```

### 15.4. Nested Subcommands

```go
// zerodoor attack pod
// zerodoor attack deployment
// zerodoor attack service

var attackPodCmd = &cobra.Command{
    Use:   "pod [name]",
    Short: "Attack a specific pod",
    Args:  cobra.ExactArgs(1),  // Yêu cầu đúng 1 argument
    Run: func(cmd *cobra.Command, args []string) {
        podName := args[0]
        fmt.Printf("Killing pod: %s\n", podName)
    },
}

var attackDeploymentCmd = &cobra.Command{
    Use:   "deployment [name]",
    Short: "Attack pods in a deployment",
    Args:  cobra.MinimumNArgs(1),
    Run: func(cmd *cobra.Command, args []string) {
        // ...
    },
}

func init() {
    attackCmd.AddCommand(attackPodCmd)
    attackCmd.AddCommand(attackDeploymentCmd)
}
```

### 15.5. main.go

```go
// main.go
package main

import "github.com/yourusername/zerodoor/cmd"

func main() {
    cmd.Execute()
}
```

### 15.6. Sử dụng

```bash
# Build
go build -o zerodoor .

# Sử dụng
./zerodoor --help
./zerodoor attack --pod nginx-123 --namespace production --type cpu
./zerodoor attack pod nginx-123 -n production
```

---

## 16. YAML/JSON & Configuration ⭐⭐⭐

### 16.1. Parsing YAML (phổ biến trong K8s)

```bash
go get gopkg.in/yaml.v3
```

```go
package main

import (
    "fmt"
    "os"
    "gopkg.in/yaml.v3"
)

// Struct tương ứng với YAML structure
type ChaosConfig struct {
    APIVersion string `yaml:"apiVersion"`
    Kind       string `yaml:"kind"`
    Metadata   struct {
        Name      string `yaml:"name"`
        Namespace string `yaml:"namespace"`
    } `yaml:"metadata"`
    Spec struct {
        Target struct {
            Selector map[string]string `yaml:"selector"`
        } `yaml:"target"`
        Attacks []struct {
            Type     string `yaml:"type"`
            Duration string `yaml:"duration"`
        } `yaml:"attacks"`
    } `yaml:"spec"`
}

func main() {
    // Đọc file YAML
    data, err := os.ReadFile("chaos.yaml")
    if err != nil {
        panic(err)
    }

    // Parse YAML → Struct
    var config ChaosConfig
    err = yaml.Unmarshal(data, &config)
    if err != nil {
        panic(err)
    }

    fmt.Printf("Chaos Experiment: %s\n", config.Metadata.Name)

    // Struct → YAML
    output, _ := yaml.Marshal(config)
    fmt.Println(string(output))
}
```

**Ví dụ file chaos.yaml:**

```yaml
apiVersion: chaos.zerodoor.io/v1
kind: ChaosExperiment
metadata:
  name: kill-nginx
  namespace: default
spec:
  target:
    selector:
      app: nginx
  attacks:
    - type: pod-kill
      duration: 30s
    - type: cpu-stress
      duration: 60s
```

### 16.2. Viper - Configuration Management ⭐

```bash
go get github.com/spf13/viper
```

```go
package main

import (
    "fmt"
    "github.com/spf13/viper"
)

type Config struct {
    Server struct {
        Port int    `mapstructure:"port"`
        Host string `mapstructure:"host"`
    } `mapstructure:"server"`
    Kubernetes struct {
        Kubeconfig string `mapstructure:"kubeconfig"`
        Namespace  string `mapstructure:"namespace"`
    } `mapstructure:"kubernetes"`
    Prometheus struct {
        URL string `mapstructure:"url"`
    } `mapstructure:"prometheus"`
}

func LoadConfig() (*Config, error) {
    viper.SetConfigName("config")        // config.yaml
    viper.SetConfigType("yaml")
    viper.AddConfigPath(".")             // Tìm trong thư mục hiện tại
    viper.AddConfigPath("/etc/zerodoor") // Hoặc /etc/zerodoor
    viper.AddConfigPath("$HOME/.zerodoor")

    // Đọc từ Environment Variables
    viper.AutomaticEnv()
    viper.SetEnvPrefix("ZERODOOR")  // ZERODOOR_SERVER_PORT=8080

    // Giá trị mặc định
    viper.SetDefault("server.port", 8080)
    viper.SetDefault("server.host", "0.0.0.0")
    viper.SetDefault("kubernetes.namespace", "default")

    if err := viper.ReadInConfig(); err != nil {
        return nil, err
    }

    var config Config
    if err := viper.Unmarshal(&config); err != nil {
        return nil, err
    }

    return &config, nil
}

func main() {
    cfg, err := LoadConfig()
    if err != nil {
        panic(err)
    }

    fmt.Printf("Server: %s:%d\n", cfg.Server.Host, cfg.Server.Port)
    fmt.Printf("K8s Namespace: %s\n", cfg.Kubernetes.Namespace)
}
```

**config.yaml:**

```yaml
server:
  port: 8080
  host: 0.0.0.0

kubernetes:
  kubeconfig: ~/.kube/config
  namespace: default

prometheus:
  url: http://prometheus:9090
```

### 16.3. Kết hợp Cobra + Viper

```go
func init() {
    cobra.OnInitialize(initConfig)
    rootCmd.PersistentFlags().StringVar(&cfgFile, "config", "", "config file")
}

func initConfig() {
    if cfgFile != "" {
        viper.SetConfigFile(cfgFile)
    }
    viper.AutomaticEnv()
    viper.ReadInConfig()
}
```

---

## 17. Docker SDK ⭐⭐

```bash
go get github.com/docker/docker/client
```

### 17.1. Kết nối Docker Engine

```go
package main

import (
    "context"
    "fmt"
    "github.com/docker/docker/api/types"
    "github.com/docker/docker/api/types/container"
    "github.com/docker/docker/client"
)

func main() {
    ctx := context.Background()

    // Tạo Docker client
    cli, err := client.NewClientWithOpts(client.FromEnv, client.WithAPIVersionNegotiation())
    if err != nil {
        panic(err)
    }
    defer cli.Close()

    // List containers
    containers, err := cli.ContainerList(ctx, container.ListOptions{All: true})
    if err != nil {
        panic(err)
    }

    for _, c := range containers {
        fmt.Printf("Container: %s, Image: %s, Status: %s\n",
            c.ID[:12], c.Image, c.Status)
    }
}
```

### 17.2. Container Operations

```go
// Stop container
err := cli.ContainerStop(ctx, containerID, container.StopOptions{})

// Start container
err := cli.ContainerStart(ctx, containerID, container.StartOptions{})

// Kill container (CHAOS!)
err := cli.ContainerKill(ctx, containerID, "SIGKILL")

// Remove container
err := cli.ContainerRemove(ctx, containerID, container.RemoveOptions{Force: true})

// Restart container
err := cli.ContainerRestart(ctx, containerID, container.StopOptions{})

// Get container logs
reader, err := cli.ContainerLogs(ctx, containerID, container.LogsOptions{
    ShowStdout: true,
    ShowStderr: true,
    Follow:     true,
})
```

### 17.3. Ví dụ: Container Killer (Chaos)

```go
func killRandomContainer(cli *client.Client, labelFilter string) error {
    ctx := context.Background()

    // List containers với filter
    containers, err := cli.ContainerList(ctx, container.ListOptions{
        Filters: filters.NewArgs(filters.Arg("label", labelFilter)),
    })
    if err != nil {
        return err
    }

    if len(containers) == 0 {
        return fmt.Errorf("no containers found with label: %s", labelFilter)
    }

    // Pick random victim
    victim := containers[rand.Intn(len(containers))]

    fmt.Printf("🔪 Killing container: %s\n", victim.ID[:12])
    return cli.ContainerKill(ctx, victim.ID, "SIGKILL")
}
```

---

## 18. Prometheus & Metrics ⭐⭐⭐

### 18.1. Prometheus Client - Expose Metrics

```bash
go get github.com/prometheus/client_golang/prometheus
go get github.com/prometheus/client_golang/prometheus/promhttp
```

```go
package main

import (
    "net/http"
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promhttp"
)

// Định nghĩa metrics
var (
    attacksTotal = prometheus.NewCounterVec(
        prometheus.CounterOpts{
            Name: "zerodoor_attacks_total",
            Help: "Total number of chaos attacks executed",
        },
        []string{"type", "target", "status"},
    )

    attackDuration = prometheus.NewHistogramVec(
        prometheus.HistogramOpts{
            Name:    "zerodoor_attack_duration_seconds",
            Help:    "Duration of chaos attacks",
            Buckets: prometheus.DefBuckets,
        },
        []string{"type"},
    )

    activeAttacks = prometheus.NewGauge(
        prometheus.GaugeOpts{
            Name: "zerodoor_active_attacks",
            Help: "Number of currently active attacks",
        },
    )
)

func init() {
    // Register metrics
    prometheus.MustRegister(attacksTotal)
    prometheus.MustRegister(attackDuration)
    prometheus.MustRegister(activeAttacks)
}

func executeAttack(attackType, target string) {
    timer := prometheus.NewTimer(attackDuration.WithLabelValues(attackType))
    defer timer.ObserveDuration()

    activeAttacks.Inc()
    defer activeAttacks.Dec()

    // Thực hiện attack...

    attacksTotal.WithLabelValues(attackType, target, "success").Inc()
}

func main() {
    // Expose metrics endpoint
    http.Handle("/metrics", promhttp.Handler())
    http.ListenAndServe(":9090", nil)
}
```

### 18.2. Query Prometheus API

```go
package main

import (
    "context"
    "fmt"
    "time"
    "github.com/prometheus/client_golang/api"
    v1 "github.com/prometheus/client_golang/api/prometheus/v1"
    "github.com/prometheus/common/model"
)

func main() {
    // Tạo Prometheus client
    client, err := api.NewClient(api.Config{
        Address: "http://prometheus:9090",
    })
    if err != nil {
        panic(err)
    }

    v1api := v1.NewAPI(client)
    ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
    defer cancel()

    // Query instant
    result, warnings, err := v1api.Query(ctx,
        `rate(container_cpu_usage_seconds_total{pod=~"nginx.*"}[5m])`,
        time.Now(),
    )
    if err != nil {
        panic(err)
    }

    // Parse result
    vector := result.(model.Vector)
    for _, sample := range vector {
        fmt.Printf("Pod: %s, CPU: %.2f\n",
            sample.Metric["pod"], float64(sample.Value))
    }
}
```

### 18.3. Alerting - Phát hiện Anomaly (Gaia Agent)

```go
func checkHighCPU(api v1.API, threshold float64) ([]string, error) {
    ctx := context.Background()

    query := fmt.Sprintf(
        `rate(container_cpu_usage_seconds_total[5m]) > %f`,
        threshold,
    )

    result, _, err := api.Query(ctx, query, time.Now())
    if err != nil {
        return nil, err
    }

    var hotPods []string
    vector := result.(model.Vector)
    for _, sample := range vector {
        podName := string(sample.Metric["pod"])
        hotPods = append(hotPods, podName)
    }

    return hotPods, nil
}
```

---

## 19. Structured Logging ⭐⭐

### 19.1. Zerolog (Recommended - Fastest)

```bash
go get github.com/rs/zerolog
```

```go
package main

import (
    "os"
    "time"
    "github.com/rs/zerolog"
    "github.com/rs/zerolog/log"
)

func main() {
    // Console output đẹp (dev mode)
    log.Logger = log.Output(zerolog.ConsoleWriter{Out: os.Stderr})

    // Hoặc JSON output (production)
    // log.Logger = zerolog.New(os.Stdout).With().Timestamp().Logger()

    // Basic logging
    log.Info().Msg("Application started")
    log.Debug().Str("config", "loaded").Msg("Configuration")
    log.Error().Err(err).Msg("Failed to connect")

    // Structured fields
    log.Info().
        Str("pod", "nginx-abc123").
        Str("namespace", "production").
        Str("action", "kill").
        Int("duration_ms", 150).
        Msg("Attack executed")

    // Sub-logger với context
    attackLog := log.With().
        Str("component", "nemesis").
        Str("experiment_id", "exp-001").
        Logger()

    attackLog.Info().Msg("Starting attack sequence")
}
```

**Output (Console):**

```
12:30:45 INF Application started
12:30:45 INF Attack executed pod=nginx-abc123 namespace=production action=kill duration_ms=150
```

**Output (JSON - Production):**

```json
{
  "level": "info",
  "pod": "nginx-abc123",
  "namespace": "production",
  "action": "kill",
  "duration_ms": 150,
  "time": "2026-02-04T12:30:45Z",
  "message": "Attack executed"
}
```

### 19.2. Slog (Go 1.21+ Standard Library)

```go
package main

import (
    "log/slog"
    "os"
)

func main() {
    // JSON handler (production)
    logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))

    // Text handler (development)
    // logger := slog.New(slog.NewTextHandler(os.Stdout, nil))

    slog.SetDefault(logger)

    slog.Info("Attack executed",
        slog.String("pod", "nginx-abc123"),
        slog.String("action", "kill"),
        slog.Int("duration_ms", 150),
    )

    // Group fields
    slog.Info("Experiment completed",
        slog.Group("target",
            slog.String("pod", "nginx"),
            slog.String("namespace", "default"),
        ),
        slog.Group("result",
            slog.Bool("success", true),
            slog.Int("mttd_seconds", 45),
        ),
    )
}
```

---

## 20. File I/O & OS Operations ⭐⭐

### 20.1. Đọc/Ghi File

```go
import (
    "os"
    "io"
    "bufio"
)

// Đọc toàn bộ file
data, err := os.ReadFile("config.yaml")

// Ghi file (tạo mới hoặc ghi đè)
err := os.WriteFile("output.txt", []byte("content"), 0644)

// Append vào file
f, err := os.OpenFile("log.txt", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
defer f.Close()
f.WriteString("new log line\n")

// Đọc file từng dòng
file, _ := os.Open("largefile.txt")
defer file.Close()
scanner := bufio.NewScanner(file)
for scanner.Scan() {
    line := scanner.Text()
    fmt.Println(line)
}
```

### 20.2. Directory Operations

```go
// Tạo directory
err := os.Mkdir("logs", 0755)
err := os.MkdirAll("path/to/deep/dir", 0755)

// List directory
entries, _ := os.ReadDir(".")
for _, entry := range entries {
    fmt.Printf("%s (dir: %v)\n", entry.Name(), entry.IsDir())
}

// Walk directory tree
filepath.WalkDir(".", func(path string, d fs.DirEntry, err error) error {
    if err != nil {
        return err
    }
    fmt.Println(path)
    return nil
})

// Remove
os.Remove("file.txt")
os.RemoveAll("directory")
```

### 20.3. Execute External Commands

```go
import "os/exec"

// Simple command
cmd := exec.Command("kubectl", "get", "pods", "-n", "default")
output, err := cmd.Output()
fmt.Println(string(output))

// Command với stdin/stdout
cmd := exec.Command("kubectl", "apply", "-f", "-")
cmd.Stdin = strings.NewReader(yamlContent)
cmd.Stdout = os.Stdout
cmd.Stderr = os.Stderr
err := cmd.Run()

// Capture both stdout and stderr
cmd := exec.Command("helm", "install", "myapp", "./chart")
var stdout, stderr bytes.Buffer
cmd.Stdout = &stdout
cmd.Stderr = &stderr
err := cmd.Run()

// Check exit code
if exitErr, ok := err.(*exec.ExitError); ok {
    fmt.Printf("Exit code: %d\n", exitErr.ExitCode())
}

// Command with timeout
ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
defer cancel()
cmd := exec.CommandContext(ctx, "long-running-command")
```

### 20.4. Environment Variables

```go
// Get
value := os.Getenv("KUBECONFIG")
value, exists := os.LookupEnv("KUBECONFIG")

// Set
os.Setenv("MY_VAR", "value")

// Get all
for _, env := range os.Environ() {
    fmt.Println(env)  // KEY=value
}
```

---

## 21. Best Practices & Patterns

### 21.1. Code Style

```go
// ✅ DO: Tên ngắn gọn, súc tích
var wg sync.WaitGroup
for i, v := range items {}
ctx context.Context

// ❌ DON'T: Tên dài dòng
var waitGroup sync.WaitGroup
for index, value := range items {}
context context.Context
```

### 21.2. Error Handling

```go
// ✅ DO: Handle error ngay
if err != nil {
    return fmt.Errorf("failed to do X: %w", err)
}

// ❌ DON'T: Bỏ qua error
result, _ := doSomething()

// ✅ DO: Early return
func process(data []byte) error {
    if len(data) == 0 {
        return errors.New("empty data")
    }

    // Happy path...
    return nil
}

// ❌ DON'T: Deep nesting
func process(data []byte) error {
    if len(data) > 0 {
        if valid(data) {
            if parsed, err := parse(data); err == nil {
                // ...
            }
        }
    }
    return nil
}
```

### 21.3. Struct Initialization

```go
// ✅ DO: Named fields
pod := Pod{
    Name:      "nginx",
    Namespace: "default",
}

// ❌ DON'T: Positional fields (dễ sai khi struct thay đổi)
pod := Pod{"nginx", "default", "Running", 3}
```

### 21.4. Interface Design

```go
// ✅ DO: Interface nhỏ (1-3 methods)
type Reader interface {
    Read(p []byte) (n int, err error)
}

type Closer interface {
    Close() error
}

// Compose interfaces
type ReadCloser interface {
    Reader
    Closer
}

// ❌ DON'T: Interface quá lớn
type DoEverything interface {
    Read()
    Write()
    Close()
    Open()
    Flush()
    Seek()
    // ...20 more methods
}
```

### 21.5. Dependency Injection

```go
// ✅ DO: Inject dependencies qua constructor
type Service struct {
    repo Repository
    log  Logger
}

func NewService(repo Repository, log Logger) *Service {
    return &Service{repo: repo, log: log}
}

// ❌ DON'T: Global variables
var globalRepo Repository

func DoSomething() {
    globalRepo.Save(...)
}
```

### 21.6. Configuration

```go
// ✅ DO: Dùng struct cho config
type Config struct {
    Host     string        `env:"HOST" default:"localhost"`
    Port     int           `env:"PORT" default:"8080"`
    Timeout  time.Duration `env:"TIMEOUT" default:"30s"`
}

// ✅ DO: Functional options pattern
type Server struct {
    host    string
    port    int
    timeout time.Duration
}

type Option func(*Server)

func WithPort(port int) Option {
    return func(s *Server) {
        s.port = port
    }
}

func WithTimeout(t time.Duration) Option {
    return func(s *Server) {
        s.timeout = t
    }
}

func NewServer(host string, opts ...Option) *Server {
    s := &Server{
        host:    host,
        port:    8080,        // default
        timeout: 30 * time.Second, // default
    }
    for _, opt := range opts {
        opt(s)
    }
    return s
}

// Usage
server := NewServer("localhost", WithPort(9090), WithTimeout(60*time.Second))
```

---

## 22. Project Structure cho Zero Door

        if valid(data) {
            if parsed, err := parse(data); err == nil {
                // ...
            }
        }
    }
    return nil

}

````

### 15.3. Struct Initialization

```go
// ✅ DO: Named fields
pod := Pod{
    Name:      "nginx",
    Namespace: "default",
}

// ❌ DON'T: Positional fields (dễ sai khi struct thay đổi)
pod := Pod{"nginx", "default", "Running", 3}
````

### 15.4. Interface Design

```go
// ✅ DO: Interface nhỏ (1-3 methods)
type Reader interface {
    Read(p []byte) (n int, err error)
}

type Closer interface {
    Close() error
}

// Compose interfaces
type ReadCloser interface {
    Reader
    Closer
}

// ❌ DON'T: Interface quá lớn
type DoEverything interface {
    Read()
    Write()
    Close()
    Open()
    Flush()
    Seek()
    // ...20 more methods
}
```

### 15.5. Dependency Injection

```go
// ✅ DO: Inject dependencies qua constructor
type Service struct {
    repo Repository
    log  Logger
}

func NewService(repo Repository, log Logger) *Service {
    return &Service{repo: repo, log: log}
}

// ❌ DON'T: Global variables
var globalRepo Repository

func DoSomething() {
    globalRepo.Save(...)
}
```

### 15.6. Configuration

```go
// ✅ DO: Dùng struct cho config
type Config struct {
    Host     string        `env:"HOST" default:"localhost"`
    Port     int           `env:"PORT" default:"8080"`
    Timeout  time.Duration `env:"TIMEOUT" default:"30s"`
}

// ✅ DO: Functional options pattern
type Server struct {
    host    string
    port    int
    timeout time.Duration
}

type Option func(*Server)

func WithPort(port int) Option {
    return func(s *Server) {
        s.port = port
    }
}

func WithTimeout(t time.Duration) Option {
    return func(s *Server) {
        s.timeout = t
    }
}

func NewServer(host string, opts ...Option) *Server {
    s := &Server{
        host:    host,
        port:    8080,        // default
        timeout: 30 * time.Second, // default
    }
    for _, opt := range opts {
        opt(s)
    }
    return s
}

// Usage
server := NewServer("localhost", WithPort(9090), WithTimeout(60*time.Second))
```

---

## 22. Project Structure cho Zero Door

```
zero-door/
├── cmd/
│   ├── nemesis/           # Agent Nemesis (Attacker)
│   │   └── main.go
│   ├── gaia/              # Agent Gaia (Detector)
│   │   └── main.go
│   └── hephaestus/        # Agent Hephaestus (Healer)
│       └── main.go
├── internal/
│   ├── attacker/          # Attack logic
│   │   ├── podkill.go
│   │   ├── cpustress.go
│   │   └── network.go
│   ├── detector/          # Detection logic
│   │   ├── prometheus.go
│   │   └── anomaly.go
│   ├── healer/            # Healing logic
│   │   ├── scaler.go
│   │   └── restarter.go
│   └── k8s/               # Kubernetes client wrapper
│       └── client.go
├── pkg/
│   └── types/             # Shared types
│       └── types.go
├── config/
│   └── config.yaml
├── deploy/
│   └── helm/
│       └── zero-door/
├── Dockerfile
├── Makefile
├── go.mod
└── go.sum
```

### Makefile Template

```makefile
.PHONY: build test run clean

# Build all agents
build:
	go build -o bin/nemesis ./cmd/nemesis
	go build -o bin/gaia ./cmd/gaia
	go build -o bin/hephaestus ./cmd/hephaestus

# Run tests
test:
	go test -v ./...

# Run with coverage
coverage:
	go test -coverprofile=coverage.out ./...
	go tool cover -html=coverage.out

# Lint
lint:
	golangci-lint run

# Clean build artifacts
clean:
	rm -rf bin/

# Build Docker images
docker:
	docker build -t zero-door/nemesis -f Dockerfile.nemesis .
	docker build -t zero-door/gaia -f Dockerfile.gaia .
	docker build -t zero-door/hephaestus -f Dockerfile.hephaestus .
```

---

## 23. DevOps Roadmap 4 Tuần ⭐⭐⭐

> **Lộ trình này được thiết kế riêng cho DevOps Engineer**, tập trung vào những gì bạn sẽ dùng hàng ngày.

### Tuần 1: Nền tảng (Foundation)

| Ngày | Nội dung                      | Thực hành                             | Output                 |
| ---- | ----------------------------- | ------------------------------------- | ---------------------- |
| 1    | Setup, Basics (Section 1-3)   | Hello World, Variables                | Chạy được `go run`     |
| 2    | Types, Struct (Section 4)     | Định nghĩa struct cho Pod, Deployment | Hiểu JSON tags         |
| 3    | Control Flow (Section 5)      | If-else, for loop, switch             | -                      |
| 4    | Functions (Section 6)         | Viết helper functions                 | Multiple return values |
| 5    | Pointers (Section 7)          | Pointer receiver methods              | Hiểu khi nào dùng `*`  |
| 6-7  | **Interfaces** (Section 8) ⭐ | Định nghĩa Attacker interface         | **Quan trọng nhất!**   |

### Tuần 2: DevOps Core Skills

| Ngày | Nội dung                        | Thực hành                  | Output                  |
| ---- | ------------------------------- | -------------------------- | ----------------------- |
| 8    | Error Handling (Section 9)      | Wrap errors, custom errors | Production-ready code   |
| 9-10 | **Concurrency** (Section 10) ⭐ | Goroutines, channels       | Parallel worker         |
| 11   | Packages & Modules (Section 11) | Tổ chức code               | Clean project structure |
| 12   | Testing (Section 12)            | Unit tests, table-driven   | Test coverage           |
| 13   | HTTP Server (Section 13)        | REST API với Gin           | `/health` endpoint      |
| 14   | HTTP Client (Section 13)        | Call external APIs         | API client              |

### Tuần 3: DevOps Tools

| Ngày  | Nội dung                          | Thực hành              | Output                    |
| ----- | --------------------------------- | ---------------------- | ------------------------- |
| 15-16 | **CLI với Cobra** (Section 15) ⭐ | Build `zerodoor` CLI   | Custom kubectl-style tool |
| 17    | **YAML/Viper** (Section 16) ⭐    | Parse K8s manifests    | Config management         |
| 18    | **Docker SDK** (Section 17)       | List/Kill containers   | Docker automation         |
| 19-20 | **Prometheus** (Section 18) ⭐    | Expose metrics + Query | Monitoring integration    |
| 21    | Structured Logging (Section 19)   | Zerolog setup          | Production logging        |

### Tuần 4: Kubernetes & Project

| Ngày  | Nội dung                                   | Thực hành                      | Output                |
| ----- | ------------------------------------------ | ------------------------------ | --------------------- |
| 22-23 | **Kubernetes client-go** (Section 14) ⭐⭐ | CRUD Pods, Watch events        | K8s automation        |
| 24    | File I/O & OS (Section 20)                 | Exec commands, env vars        | Scripting in Go       |
| 25-26 | Best Practices (Section 21)                | Refactor code                  | Clean code            |
| 27-28 | **Final Project**                          | Build Nemesis Agent hoàn chỉnh | Production-ready tool |

---

### 🎯 Skill Matrix cho DevOps Engineer

```
                        IMPORTANCE FOR DEVOPS
                    Low ──────────────────────► High

 ┌──────────────────────────────────────────────────────┐
 │  Basics          ████████░░░░░░░░░░░░ (Must know)    │
 │  Interfaces      ████████████████████ (Critical!)   │
 │  Concurrency     ████████████████████ (Critical!)   │
 │  HTTP/REST       ████████████████░░░░ (Very High)   │
 │  CLI/Cobra       ████████████████████ (Critical!)   │
 │  YAML/Config     ████████████████████ (Critical!)   │
 │  Docker SDK      ████████████████░░░░ (Very High)   │
 │  Kubernetes      ████████████████████ (Critical!)   │
 │  Prometheus      ████████████████░░░░ (Very High)   │
 │  Logging         ████████████████░░░░ (Very High)   │
 │  Testing         ████████████░░░░░░░░ (Important)   │
 │  Generics        ████████░░░░░░░░░░░░ (Nice to have)│
 └──────────────────────────────────────────────────────┘
```

---

### 💼 Sau khi hoàn thành, bạn có thể:

| Skill                 | Ứng dụng thực tế                          |
| --------------------- | ----------------------------------------- |
| **CLI Tools**         | Viết kubectl plugins, custom DevOps tools |
| **K8s Automation**    | Operators, Controllers, CRDs              |
| **Docker Automation** | CI/CD pipelines, container management     |
| **Monitoring**        | Custom exporters, alerting tools          |
| **Config Management** | Helm chart generators, config validators  |

---

## 📚 Tài liệu Tham khảo

| Nguồn                   | Link                                                         | Ghi chú                         |
| ----------------------- | ------------------------------------------------------------ | ------------------------------- |
| **Go Tour**             | https://go.dev/tour                                          | Interactive tutorial chính thức |
| **Effective Go**        | https://go.dev/doc/effective_go                              | Best practices từ Go team       |
| **Go by Example**       | https://gobyexample.com                                      | Ví dụ code từng concept         |
| **client-go Examples**  | https://github.com/kubernetes/client-go/tree/master/examples | K8s code samples                |
| **Uber Go Style Guide** | https://github.com/uber-go/guide                             | Industry-grade style guide      |
| **Cobra Documentation** | https://cobra.dev                                            | CLI framework docs              |
| **Viper Documentation** | https://github.com/spf13/viper                               | Config management               |

---

## 🔥 Quick Reference - DevOps Commands

```bash
# === Project Setup ===
go mod init github.com/username/project
go mod tidy
go get -u ./...

# === Build ===
go build -o bin/app ./cmd/app
CGO_ENABLED=0 GOOS=linux go build -o app .  # For Docker

# === Test ===
go test ./...
go test -v -cover ./...
go test -race ./...  # Race condition detection

# === Lint ===
golangci-lint run
go vet ./...

# === Dependencies ===
go list -m all
go mod why <package>
go mod graph

# === Cross-compile ===
GOOS=linux GOARCH=amd64 go build -o app-linux .
GOOS=darwin GOARCH=arm64 go build -o app-mac .
GOOS=windows GOARCH=amd64 go build -o app.exe .
```

---

**Chúc bạn thành công với Go và sự nghiệp DevOps! 🚀**
