package skills

import (
	"strings"
)

type Skill interface {
	Match(intent string) bool
	Execute(intent string) error
	Name() string
}

var Registry []Skill

func Register(s Skill) {
	Registry = append(Registry, s)
}

func MatchIntent(intent string) Skill {
	for _, s := range Registry {
		if s.Match(intent) {
			return s
		}
	}
	return nil
}

// Helper to check if a string contains all keywords
func ContainsAllKeywords(intent string, keywords ...string) bool {
	lower := strings.ToLower(intent)
	for _, kw := range keywords {
		if !strings.Contains(lower, kw) {
			return false
		}
	}
	return true
}
