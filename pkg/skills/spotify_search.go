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
	return ContainsAllKeywords(intent, "play", "spotify") || 
	       ContainsAllKeywords(intent, "search", "spotify")
}

func (s *SpotifySearchSkill) Execute(intent string) error {
	fmt.Println("Executing Advanced Skill: SpotifySearch")
	
	searchTerm := "Sarthak Goswami" // fallback
	if idx := strings.Index(intent, "search for"); idx != -1 {
		searchTerm = strings.TrimSpace(intent[idx+10:])
		searchTerm = strings.TrimSuffix(searchTerm, "on spotify")
	} else if idx := strings.Index(intent, "play"); idx != -1 {
		part := strings.TrimSpace(intent[idx+4:])
		searchTerm = strings.TrimPrefix(part, "on spotify")
		searchTerm = strings.TrimSuffix(searchTerm, "on spotify")
		searchTerm = strings.TrimSpace(searchTerm)
	}
	
	// The Spotify Web Player URI for searching
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
