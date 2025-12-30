import type { LeaderboardProps } from '../types';
import styles from './Leaderboard.module.css';

function formatDate(timestamp: number): string {
  const date = new Date(timestamp);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

export function Leaderboard({ entries, currentPlayerEntry, onClose }: LeaderboardProps) {
  const currentEntryRank = currentPlayerEntry
    ? entries.findIndex((e) => e.id === currentPlayerEntry.id) + 1
    : null;

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <button className={styles.closeButton} onClick={onClose} aria-label="Close leaderboard">
          ×
        </button>

        <h2 className={styles.title}>Leaderboard</h2>
        <p className={styles.subtitle}>Top 10 Meme Experts</p>

        {entries.length === 0 ? (
          <div className={styles.emptyState}>
            <p>No scores yet!</p>
            <p className={styles.emptyHint}>Be the first to make it on the board.</p>
          </div>
        ) : (
          <>
            {currentPlayerEntry && currentEntryRank && (
              <div className={styles.yourScore}>
                <span className={styles.yourScoreLabel}>Your Rank</span>
                <span className={styles.yourScoreRank}>#{currentEntryRank}</span>
              </div>
            )}

            <div className={styles.tableContainer}>
              <table className={styles.table}>
                <thead>
                  <tr>
                    <th className={styles.rankHeader}>Rank</th>
                    <th className={styles.nameHeader}>Player</th>
                    <th className={styles.scoreHeader}>Score</th>
                    <th className={styles.dateHeader}>Date</th>
                  </tr>
                </thead>
                <tbody>
                  {entries.map((entry, index) => {
                    const rank = index + 1;
                    const isCurrentPlayer = currentPlayerEntry?.id === entry.id;
                    return (
                      <tr
                        key={entry.id}
                        className={`${styles.row} ${isCurrentPlayer ? styles.currentPlayer : ''}`}
                      >
                        <td className={styles.rank}>
                          {rank <= 3 ? (
                            <span className={`${styles.medal} ${styles[`medal${rank}`]}`}>
                              {rank === 1 ? '🥇' : rank === 2 ? '🥈' : '🥉'}
                            </span>
                          ) : (
                            <span className={styles.rankNumber}>{rank}</span>
                          )}
                        </td>
                        <td className={styles.name}>
                          {entry.playerName}
                          {isCurrentPlayer && <span className={styles.youBadge}>You</span>}
                        </td>
                        <td className={styles.score}>{entry.score}</td>
                        <td className={styles.date}>{formatDate(entry.timestamp)}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
