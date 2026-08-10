package main
import (
    "fmt"
    "forge/pkg/uia"
)
func main() {
    out, _ := uia.DumpUI()
    fmt.Println(len(out))
}
