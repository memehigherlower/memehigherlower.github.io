import { useEffect, useState, useCallback } from 'react';
import type { Meme, LeaderboardEntry } from '../types';
import { useGameState } from '../hooks/useGameState';
import { useHighScore } from '../hooks/useHighScore';
import { useLeaderboard } from '../hooks/useLeaderboard';
import { StartScreen } from './StartScreen';
import { MemeComparison } from './MemeComparison';
import { ScoreDisplay } from './ScoreDisplay';
import { GameOverModal } from './GameOverModal';
import { Leaderboard } from './Leaderboard';
import styles from './GameContainer.module.css';

interface GameContainerProps {
  memes: Meme[];
}

export function GameContainer({ memes }: GameContainerProps) {
  const { highScore, updateHighScore } = useHighScore();
  const { state, startGame, guessHigher, guessLower, playAgain } = useGameState(memes, highScore);
  const { entries, addEntry, getPlayerRank } = useLeaderboard();

  const [showLeaderboard, setShowLeaderboard] = useState(false);
  const [currentGameEntry, setCurrentGameEntry] = useState<LeaderboardEntry | null>(null);
  const [hasSubmittedScore, setHasSubmittedScore] = useState(false);

  // Update high score when game ends
  useEffect(() => {
    if (state.phase === 'gameover') {
      updateHighScore(state.currentStreak);
    }
  }, [state.phase, state.currentStreak, updateHighScore]);

  // Reset submission state when starting a new game
  useEffect(() => {
    if (state.phase === 'playing') {
      setCurrentGameEntry(null);
      setHasSubmittedScore(false);
    }
  }, [state.phase]);

  const handleSubmitScore = useCallback(
    (playerName: string) => {
      const entry = addEntry(playerName, state.currentStreak);
      if (entry) {
        setCurrentGameEntry(entry);
        setHasSubmittedScore(true);
      }
    },
    [addEntry, state.currentStreak]
  );

  const handleViewLeaderboard = useCallback(() => {
    setShowLeaderboard(true);
  }, []);

  const handleCloseLeaderboard = useCallback(() => {
    setShowLeaderboard(false);
  }, []);

  const isNewHighScore = state.currentStreak > highScore;
  const showComparisonViewCount = state.phase === 'revealing' || state.lastGuessCorrect !== null;
  const revealResult = state.lastGuessCorrect === true
    ? 'correct'
    : state.lastGuessCorrect === false
    ? 'incorrect'
    : null;

  const playerRank = currentGameEntry ? getPlayerRank(currentGameEntry.id) : null;

  return (
    <div className={styles.container}>
      {state.phase === 'start' && (
        <StartScreen onStart={startGame} highScore={highScore} />
      )}

      {(state.phase === 'playing' || state.phase === 'revealing') &&
        state.currentMeme &&
        state.comparisonMeme && (
          <>
            <header className={styles.header}>
              <h1 className={styles.title}>Meme Higher or Lower</h1>
              <ScoreDisplay currentStreak={state.currentStreak} highScore={highScore} />
            </header>

            <main className={styles.main}>
              <MemeComparison
                currentMeme={state.currentMeme}
                comparisonMeme={state.comparisonMeme}
                showComparisonViewCount={showComparisonViewCount}
                isRevealing={state.phase === 'revealing'}
                revealResult={revealResult}
                onGuessHigher={guessHigher}
                onGuessLower={guessLower}
              />
            </main>

            <footer className={styles.footer}>
              <p className={styles.hint}>
                Does <strong>{state.comparisonMeme.name}</strong> have more or fewer page views than{' '}
                <strong>{state.currentMeme.name}</strong>?
              </p>
            </footer>
          </>
        )}

      {state.phase === 'gameover' && (
        <GameOverModal
          finalScore={state.currentStreak}
          highScore={Math.max(highScore, state.currentStreak)}
          isNewHighScore={isNewHighScore}
          onPlayAgain={playAgain}
          onSubmitScore={handleSubmitScore}
          onViewLeaderboard={handleViewLeaderboard}
          hasSubmittedScore={hasSubmittedScore}
          playerRank={playerRank}
        />
      )}

      {showLeaderboard && (
        <Leaderboard
          entries={entries}
          currentPlayerEntry={currentGameEntry}
          onClose={handleCloseLeaderboard}
        />
      )}
    </div>
  );
}
