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
	var bestSkill Skill
	bestScore := 9999

	for _, s := range Registry {
		if ds, ok := s.(*DynamicSkill); ok {
			match, score := FuzzyMatchWithScore(intent, ds.SkillName)
			if match && score < bestScore {
				bestScore = score
				bestSkill = s
			}
		} else {
			// Advanced skill
			if s.Match(intent) {
				return s // Advanced skills always win if they match
			}
		}
	}
	return bestSkill
}

// Helper to check if a string contains all keywords
func ContainsAllKeywords(intent string, keywords ...string) bool {
	inputTokens := strings.Fields(strings.ToLower(intent))
	
	for _, kw := range keywords {
		kw = strings.ToLower(kw)
		found := false
		
		for _, iToken := range inputTokens {
			dist := levenshtein(iToken, kw)
			// Much stricter typos for exact keyword constraints in advanced skills
			allowedTypos := 0
			if len(kw) >= 5 {
				allowedTypos = 1
			}
			if dist <= allowedTypos {
				found = true
				break
			}
		}
		
		if !found && !strings.Contains(strings.ToLower(intent), kw) {
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

// levenshtein computes the Levenshtein distance between two strings
func levenshtein(s1, s2 string) int {
	lenS1 := len(s1)
	lenS2 := len(s2)
	
	if lenS1 == 0 {
		return lenS2
	}
	if lenS2 == 0 {
		return lenS1
	}

	matrix := make([][]int, lenS1+1)
	for i := range matrix {
		matrix[i] = make([]int, lenS2+1)
	}

	for i := 0; i <= lenS1; i++ {
		matrix[i][0] = i
	}
	for j := 0; j <= lenS2; j++ {
		matrix[0][j] = j
	}

	for i := 1; i <= lenS1; i++ {
		for j := 1; j <= lenS2; j++ {
			cost := 1
			if s1[i-1] == s2[j-1] {
				cost = 0
			}
			matrix[i][j] = min(
				matrix[i-1][j]+1,      // deletion
				matrix[i][j-1]+1,      // insertion
				matrix[i-1][j-1]+cost, // substitution
			)
		}
	}
	return matrix[lenS1][lenS2]
}

func min(a, b, c int) int {
	m := a
	if b < m {
		m = b
	}
	if c < m {
		m = c
	}
	return m
}

func FuzzyMatchWithScore(input, target string) (bool, int) {
	input = strings.ToLower(input)
	target = strings.ToLower(target)
	
	if input == target {
		return true, 0
	}
	if strings.Contains(input, target) && len(input) == len(target) {
		return true, 0
	}

	inputTokens := strings.Fields(input)
	targetTokens := strings.Fields(target)

	matchCount := 0
	totalScore := 0
	
	for _, tToken := range targetTokens {
		bestDist := 999
		for _, iToken := range inputTokens {
			dist := levenshtein(iToken, tToken)
			if dist < bestDist {
				bestDist = dist
			}
		}
		
		allowedTypos := 0
		if len(tToken) >= 5 {
			allowedTypos = 1
		}
		if len(tToken) >= 8 {
			allowedTypos = 2
		}
		
		if bestDist <= allowedTypos {
			matchCount++
			totalScore += bestDist
		} else {
			totalScore += 100 // penalty for missing word
		}
	}

	// Calculate a penalty for extra words in the input that didn't match anything
	extraWords := len(inputTokens) - matchCount
	if extraWords > 0 {
		totalScore += extraWords * 10 
	}

	// Must match all target tokens to be considered a match
	isMatch := (matchCount == len(targetTokens) && len(targetTokens) > 0)
	
	// Ensure that extra words don't allow a 1-word target to greedily consume a multi-word input
	// unless the score is exceptionally good. 
	if isMatch && extraWords > 0 && len(targetTokens) == 1 {
		// If input is "open spotify" (2 tokens) and target is "openai" (1 token)
		// totalScore = distance("open", "openai") + 1*10 = 2 + 10 = 12.
		// We can add a strict check: if it's a 1-word target but input has >1 word, it shouldn't match
		// unless it's explicitly containing the target.
		if !strings.Contains(input, target) {
			isMatch = false
		}
	}
	
	return isMatch, totalScore
}

func (s *DynamicSkill) Match(intent string) bool {
	// We no longer use this directly in MatchIntent, but keep it for interface satisfaction
	match, _ := FuzzyMatchWithScore(intent, s.SkillName)
	return match
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
