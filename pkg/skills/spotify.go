package skills

import (
	"fmt"
	"forge/pkg/executor"
	"strings"
)

type SpotifySearchSkill struct{}

func init() {
	Register(&SpotifySearchSkill{})
}

func (s *SpotifySearchSkill) Name() string {
	return "SpotifySearch"
}

func (s *SpotifySearchSkill) Match(intent string) bool {
	if strings.Contains(intent, "opened") || strings.Contains(intent, "this") || 
	   strings.Contains(intent, "click") || strings.Contains(intent, "screen") {
		return false
	}
	
	return ContainsAllKeywords(intent, "spotify", "search") || 
	       ContainsAllKeywords(intent, "play", "spotify") ||
	       ContainsAllKeywords(intent, "spotify", "play")
}

func (s *SpotifySearchSkill) Execute(intent string) error {
	fmt.Println("Executing Advanced Skill: SpotifySearch")
	
	searchTerm := "Judas" // default fallback
	lower := strings.ToLower(intent)

	if idx := strings.Index(lower, "search for"); idx != -1 {
		searchTerm = strings.TrimSpace(intent[idx+10:])
		searchTerm = strings.TrimSuffix(searchTerm, "on spotify")
		searchTerm = strings.TrimSuffix(searchTerm, "in spotify")
		searchTerm = strings.TrimSpace(searchTerm)
	} else if idx := strings.Index(lower, "play"); idx != -1 {
		part := strings.TrimSpace(intent[idx+4:])
		part = strings.TrimSuffix(part, "on spotify")
		part = strings.TrimSuffix(part, "in spotify")
		searchTerm = strings.TrimSpace(part)
	}

	actions := []executor.Action{
		// 1. Open Spotify via Start Menu
		{Type: "key", Key: "win"},
		{Type: "sleep", Ms: 1000},
		{Type: "type", Text: "spotify"},
		{Type: "sleep", Ms: 1000},
		{Type: "key", Key: "enter"},
		{Type: "sleep", Ms: 3000},
		
		// 2. Focus Spotify Search Bar (Ctrl+L or Ctrl+K)
		{Type: "key", Key: "ctrl+k"},
		{Type: "sleep", Ms: 1000},
		
		// 3. Type search term and hit enter
		{Type: "type", Text: searchTerm},
		{Type: "sleep", Ms: 1000},
		{Type: "key", Key: "enter"},
	}
	
	executor.ExecutePlan(actions)
	return nil
}
