import { useState } from 'react';
import type { GameOverModalProps } from '../types';
import styles from './GameOverModal.module.css';

export function GameOverModal({
  finalScore,
  highScore,
  isNewHighScore,
  onPlayAgain,
  onSubmitScore,
  onViewLeaderboard,
  hasSubmittedScore,
  playerRank,
}: GameOverModalProps) {
  const [playerName, setPlayerName] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (playerName.trim() && !isSubmitting) {
      setIsSubmitting(true);
      onSubmitScore(playerName.trim());
    }
  };

  const canSubmitScore = finalScore > 0 && !hasSubmittedScore;

  return (
    <div className={styles.overlay}>
      <div className={styles.modal}>
        {isNewHighScore && (
          <div className={styles.newHighScoreBanner}>
            New High Score!
          </div>
        )}

        <h2 className={styles.title}>Game Over</h2>

        <div className={styles.scoreContainer}>
          <div className={styles.scoreBox}>
            <span className={styles.scoreLabel}>Final Score</span>
            <span className={`${styles.scoreValue} ${isNewHighScore ? styles.highlight : ''}`}>
              {finalScore}
            </span>
          </div>

          <div className={styles.scoreBox}>
            <span className={styles.scoreLabel}>High Score</span>
            <span className={styles.scoreValue}>{highScore}</span>
          </div>
        </div>

        <p className={styles.message}>
          {finalScore === 0
            ? "Better luck next time!"
            : finalScore < 5
            ? "Good effort! Keep practicing!"
            : finalScore < 10
            ? "Nice streak! You know your memes!"
            : "Amazing! You're a meme expert!"}
        </p>

        {canSubmitScore && (
          <form className={styles.nameForm} onSubmit={handleSubmit}>
            <label className={styles.nameLabel}>Enter your name for the leaderboard</label>
            <div className={styles.nameInputGroup}>
              <input
                type="text"
                className={styles.nameInput}
                value={playerName}
                onChange={(e) => setPlayerName(e.target.value)}
                placeholder="Your name"
                maxLength={20}
                autoFocus
              />
              <button
                type="submit"
                className={styles.submitButton}
                disabled={!playerName.trim() || isSubmitting}
              >
                Submit
              </button>
            </div>
          </form>
        )}

        {hasSubmittedScore && playerRank && (
          <div className={styles.rankDisplay}>
            You ranked <span className={styles.rankNumber}>#{playerRank}</span> on the leaderboard!
          </div>
        )}

        <div className={styles.buttonGroup}>
          <button className={styles.playAgainButton} onClick={onPlayAgain}>
            Play Again
          </button>
          <button className={styles.leaderboardButton} onClick={onViewLeaderboard}>
            View Leaderboard
          </button>
        </div>
      </div>
    </div>
  );
}
