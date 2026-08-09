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

	safeSearch := strings.ReplaceAll(searchTerm, " ", "%20")
	targetUrl := "https://open.spotify.com/search/" + safeSearch
	
	actions := []executor.Action{
		{Type: "key", Key: "win+r"},
		{Type: "sleep", Ms: 1000},
		{Type: "type", Text: "brave " + targetUrl},
		{Type: "sleep", Ms: 1000},
		{Type: "key", Key: "enter"},
		
		// The user explicitly requested a 3 second delay for loading apps
		{Type: "sleep", Ms: 3000},
		
		// To play the top result in Spotify search:
		// Usually we can press Tab a few times to focus "Top result" and hit enter.
		{Type: "key", Key: "tab"},
		{Type: "sleep", Ms: 200},
		{Type: "key", Key: "tab"},
		{Type: "sleep", Ms: 200},
		{Type: "key", Key: "tab"},
		{Type: "sleep", Ms: 200},
		{Type: "key", Key: "tab"},
		{Type: "sleep", Ms: 200},
		{Type: "key", Key: "enter"},
	}
	
	executor.ExecutePlan(actions)
	return nil
}
