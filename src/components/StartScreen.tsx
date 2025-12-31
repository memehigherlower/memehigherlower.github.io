import styles from './StartScreen.module.css';

interface StartScreenProps {
  onStart: () => void;
  onViewLeaderboard: () => void;
  highScore: number;
}

export function StartScreen({ onStart, onViewLeaderboard, highScore }: StartScreenProps) {
  return (
    <div className={styles.container}>
      <div className={styles.content}>
        <h1 className={styles.title}>
          Meme<br />
          <span className={styles.highlight}>Higher or Lower</span>
        </h1>

        <p className={styles.description}>
          Guess which meme has more page views on KnowYourMeme.
          <br />
          How long can you keep your streak going?
        </p>

        <div className={styles.instructions}>
          <div className={styles.instruction}>
            <span className={styles.instructionNumber}>1</span>
            <span>You'll see two memes side by side</span>
          </div>
          <div className={styles.instruction}>
            <span className={styles.instructionNumber}>2</span>
            <span>Guess if the second meme has higher or lower page views</span>
          </div>
          <div className={styles.instruction}>
            <span className={styles.instructionNumber}>3</span>
            <span>Get it right to continue your streak!</span>
          </div>
        </div>

        {highScore > 0 && (
          <div className={styles.highScore}>
            Your High Score: <span className={styles.highScoreValue}>{highScore}</span>
          </div>
        )}

        <div className={styles.buttonGroup}>
          <button className={styles.playButton} onClick={onStart}>
            Play Now
          </button>
          <button className={styles.leaderboardButton} onClick={onViewLeaderboard}>
            View Leaderboard
          </button>
        </div>
      </div>
    </div>
  );
}
