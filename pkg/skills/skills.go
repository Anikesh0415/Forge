package skills

import (
	"encoding/json"
	"fmt"
	"forge/pkg/executor"
	"os"
	"path/filepath"
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

type DynamicSkill struct {
	SkillName string            `json:"name"`
	Actions   []executor.Action `json:"actions"`
}

func (s *DynamicSkill) Name() string {
	return s.SkillName
}

func (s *DynamicSkill) Match(intent string) bool {
	return intent == strings.ToLower(s.SkillName)
}

func (s *DynamicSkill) Execute(intent string) error {
	fmt.Printf("Executing Learned Skill: %s\n", s.SkillName)
	executor.ExecutePlan(s.Actions)
	return nil
}

func LoadLearnedSkills() {
	dbPath := "skills_db"
	if _, err := os.Stat(dbPath); os.IsNotExist(err) {
		os.Mkdir(dbPath, 0755)
		return
	}

	files, err := os.ReadDir(dbPath)
	if err != nil {
		fmt.Printf("Error reading skills_db: %v\n", err)
		return
	}

	for _, file := range files {
		if strings.HasSuffix(file.Name(), ".json") {
			content, err := os.ReadFile(filepath.Join(dbPath, file.Name()))
			if err != nil {
				continue
			}

			var skill DynamicSkill
			if err := json.Unmarshal(content, &skill); err == nil {
				Register(&skill)
				fmt.Printf("Loaded learned skill: %s\n", skill.SkillName)
			}
		}
	}
}
