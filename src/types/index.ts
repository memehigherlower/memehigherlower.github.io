export interface Meme {
  id: string;
  name: string;
  views: number;
  imageUrl: string;
  fallbackImageUrl?: string;
  description?: string;
  kymUrl: string;
  year?: number;
  category?: string;
}

export type GamePhase = 'start' | 'playing' | 'revealing' | 'gameover';

export interface GameState {
  phase: GamePhase;
  currentMeme: Meme | null;
  comparisonMeme: Meme | null;
  currentStreak: number;
  highScore: number;
  usedMemeIds: Set<string>;
  lastGuessCorrect: boolean | null;
}

export type GameAction =
  | { type: 'START_GAME'; payload: { currentMeme: Meme; comparisonMeme: Meme } }
  | { type: 'GUESS'; payload: { guess: 'higher' | 'lower' } }
  | { type: 'REVEAL_RESULT'; payload: { isCorrect: boolean } }
  | { type: 'NEXT_ROUND'; payload: { newMeme: Meme } }
  | { type: 'GAME_OVER' }
  | { type: 'RESET' };

export interface MemeCardProps {
  meme: Meme;
  showViewCount: boolean;
  isReference: boolean;
  onGuessHigher?: () => void;
  onGuessLower?: () => void;
  isRevealing?: boolean;
  revealResult?: 'correct' | 'incorrect' | null;
}

export interface GameOverModalProps {
  finalScore: number;
  highScore: number;
  isNewHighScore: boolean;
  onPlayAgain: () => void;
  onSubmitScore: (playerName: string) => void;
  onViewLeaderboard: () => void;
  hasSubmittedScore: boolean;
  playerRank: number | null;
}

export interface ScoreDisplayProps {
  currentStreak: number;
  highScore: number;
}

export interface LeaderboardEntry {
  id: string;
  playerName: string;
  score: number;
  timestamp: number;
}

export interface LeaderboardProps {
  entries: LeaderboardEntry[];
  currentPlayerEntry?: LeaderboardEntry | null;
  onClose: () => void;
}
