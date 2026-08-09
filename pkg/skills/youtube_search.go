package skills

import (
	"fmt"
	"forge/pkg/executor"
	"strings"
)

type YouTubeSearchSkill struct{}

func init() {
	Register(&YouTubeSearchSkill{})
}

func (s *YouTubeSearchSkill) Name() string {
	return "YouTubeSearch"
}

func (s *YouTubeSearchSkill) Match(intent string) bool {
	return ContainsAllKeywords(intent, "youtube", "search") || 
	       ContainsAllKeywords(intent, "play", "youtube")
}

func (s *YouTubeSearchSkill) Execute(intent string) error {
	fmt.Println("Executing Advanced Skill: YouTubeSearch")
	
	// Extremely naive extraction for demonstration.
	// "open youtube and search for sarthak goswami" -> "sarthak goswami"
	searchTerm := "Sarthak Goswami" // fallback
	if idx := strings.Index(intent, "search for"); idx != -1 {
		searchTerm = strings.TrimSpace(intent[idx+10:])
	} else if idx := strings.Index(intent, "play"); idx != -1 {
		part := strings.TrimSpace(intent[idx+4:])
		searchTerm = strings.TrimPrefix(part, "on youtube")
		searchTerm = strings.TrimSuffix(searchTerm, "on youtube")
		searchTerm = strings.TrimSpace(searchTerm)
	}
	
	actions := []executor.Action{
		// 1. Open Edge/Chrome (Default browser via run prompt)
		{Type: "key", Key: "win"},
		{Type: "sleep", Ms: 1000},
		{Type: "type", Text: "edge"},
		{Type: "sleep", Ms: 1000},
		{Type: "key", Key: "enter"},
		{Type: "sleep", Ms: 3000},
		
		// 2. Focus address bar and navigate to youtube search directly
		{Type: "type", Text: "https://www.youtube.com/results?search_query=" + strings.ReplaceAll(searchTerm, " ", "+")},
		{Type: "sleep", Ms: 500},
		{Type: "key", Key: "enter"},
	}
	
	executor.ExecutePlan(actions)
	return nil
}
