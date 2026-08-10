package skills

import (
	"fmt"
	"forge/pkg/executor"
	"forge/pkg/uia"
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
	}
	
	executor.ExecutePlan(actions)
	
	// Use closed-loop UIA watcher to wait for the page to load, instead of blind sleep
	fmt.Println("Waiting for Spotify Play button via UIA...")
	
	// In Spotify Web Player, the play button usually has an aria-label like "Play Judas" or just "Play"
	el, err := uia.WaitForElement("Play " + searchTerm, 10000)
	if err != nil {
		el, err = uia.WaitForElement("Play", 5000)
	}
	
	if err == nil && el != nil {
		fmt.Printf("Found Play button at %d, %d\n", el.X, el.Y)
		executor.ExecutePlan([]executor.Action{
			{Type: "move", X: el.X, Y: el.Y},
			{Type: "sleep", Ms: 200},
			{Type: "click"},
		})
	} else {
		fmt.Println("Could not find Play button, playback failed.")
	}
	
	return nil
}
