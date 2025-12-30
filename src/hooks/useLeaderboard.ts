import { useState, useCallback, useEffect } from 'react';
import type { LeaderboardEntry } from '../types';

const STORAGE_KEY = 'meme-higher-lower-leaderboard';
const MAX_ENTRIES = 10;
const MAX_NAME_LENGTH = 20;
const MAX_REASONABLE_SCORE = 176; // Total number of memes in the game

function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

function sanitizeName(name: string): string {
  return name
    .trim()
    .slice(0, MAX_NAME_LENGTH)
    .replace(/[<>]/g, ''); // Basic XSS prevention
}

function isValidScore(score: number): boolean {
  return (
    typeof score === 'number' &&
    Number.isInteger(score) &&
    score >= 0 &&
    score <= MAX_REASONABLE_SCORE
  );
}

function loadLeaderboard(): LeaderboardEntry[] {
  if (typeof window === 'undefined') return [];
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return [];
    const parsed = JSON.parse(stored);
    if (!Array.isArray(parsed)) return [];
    // Validate and filter entries
    return parsed
      .filter(
        (entry): entry is LeaderboardEntry =>
          entry &&
          typeof entry.id === 'string' &&
          typeof entry.playerName === 'string' &&
          typeof entry.score === 'number' &&
          typeof entry.timestamp === 'number' &&
          isValidScore(entry.score)
      )
      .slice(0, MAX_ENTRIES);
  } catch {
    return [];
  }
}

function saveLeaderboard(entries: LeaderboardEntry[]): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(entries.slice(0, MAX_ENTRIES)));
  } catch {
    // localStorage might not be available or full
  }
}

export function useLeaderboard() {
  const [entries, setEntries] = useState<LeaderboardEntry[]>(loadLeaderboard);
  const [lastAddedEntry, setLastAddedEntry] = useState<LeaderboardEntry | null>(null);

  // Sync to localStorage when entries change
  useEffect(() => {
    saveLeaderboard(entries);
  }, [entries]);

  const addEntry = useCallback((playerName: string, score: number): LeaderboardEntry | null => {
    // Validate inputs
    if (!isValidScore(score)) {
      console.warn('Invalid score rejected:', score);
      return null;
    }

    const sanitizedName = sanitizeName(playerName);
    if (!sanitizedName) {
      return null;
    }

    const newEntry: LeaderboardEntry = {
      id: generateId(),
      playerName: sanitizedName,
      score,
      timestamp: Date.now(),
    };

    setEntries((prev) => {
      const updated = [...prev, newEntry]
        // Sort by score (desc), then by timestamp (asc for ties - earlier is better)
        .sort((a, b) => {
          if (b.score !== a.score) return b.score - a.score;
          return a.timestamp - b.timestamp;
        })
        .slice(0, MAX_ENTRIES);
      return updated;
    });

    setLastAddedEntry(newEntry);
    return newEntry;
  }, []);

  const getPlayerRank = useCallback(
    (entryId: string): number | null => {
      const index = entries.findIndex((e) => e.id === entryId);
      return index >= 0 ? index + 1 : null;
    },
    [entries]
  );

  const isScoreWorthy = useCallback(
    (score: number): boolean => {
      if (score <= 0) return false;
      if (entries.length < MAX_ENTRIES) return true;
      const lowestScore = entries[entries.length - 1]?.score ?? 0;
      return score > lowestScore;
    },
    [entries]
  );

  const clearLeaderboard = useCallback(() => {
    setEntries([]);
    setLastAddedEntry(null);
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch {
      // Ignore
    }
  }, []);

  return {
    entries,
    lastAddedEntry,
    addEntry,
    getPlayerRank,
    isScoreWorthy,
    clearLeaderboard,
  };
}
