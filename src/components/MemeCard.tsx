import { useState } from 'react';
import type { MemeCardProps } from '../types';
import { formatNumber } from '../utils/formatNumber';
import styles from './MemeCard.module.css';
import '../styles/animations.css';

export function MemeCard({
  meme,
  showViewCount,
  isReference,
  onGuessHigher,
  onGuessLower,
  isRevealing,
  revealResult,
}: MemeCardProps) {
  const [imageError, setImageError] = useState(false);
  const [imageLoaded, setImageLoaded] = useState(false);

  const handleImageError = () => {
    if (!imageError && meme.fallbackImageUrl) {
      setImageError(true);
    }
  };

  const baseUrl = import.meta.env.BASE_URL.endsWith('/')
    ? import.meta.env.BASE_URL.slice(0, -1)
    : import.meta.env.BASE_URL;
  const rawImageUrl = imageError && meme.fallbackImageUrl ? meme.fallbackImageUrl : meme.imageUrl;
  const imageUrl = rawImageUrl.startsWith('/') ? `${baseUrl}${rawImageUrl}` : rawImageUrl;

  const cardClass = [
    styles.card,
    revealResult === 'correct' ? styles.correct : '',
    revealResult === 'incorrect' ? styles.incorrect : '',
    isRevealing ? styles.revealing : '',
  ].filter(Boolean).join(' ');

  return (
    <div className={cardClass}>
      <div className={styles.imageContainer}>
        {!imageLoaded && (
          <div className={styles.imagePlaceholder}>
            <div className={styles.spinner} />
          </div>
        )}
        <img
          src={imageUrl}
          alt={meme.name}
          className={`${styles.image} ${imageLoaded ? styles.imageLoaded : ''}`}
          onError={handleImageError}
          onLoad={() => setImageLoaded(true)}
          loading="lazy"
        />
      </div>

      <div className={styles.content}>
        <h2 className={styles.title}>{meme.name}</h2>

        {meme.description && (
          <p className={styles.description}>{meme.description}</p>
        )}

        {showViewCount && (
          <div className={`${styles.viewCount} ${isRevealing ? 'animate-count-up' : ''}`}>
            <span className={styles.viewLabel}>Page Views</span>
            <span className={styles.viewNumber}>{formatNumber(meme.views)}</span>
          </div>
        )}

        {!isReference && !showViewCount && onGuessHigher && onGuessLower && (
          <div className={styles.buttonGroup}>
            <button
              className={`${styles.button} ${styles.buttonHigher}`}
              onClick={onGuessHigher}
              disabled={isRevealing}
            >
              Higher
            </button>
            <button
              className={`${styles.button} ${styles.buttonLower}`}
              onClick={onGuessLower}
              disabled={isRevealing}
            >
              Lower
            </button>
          </div>
        )}

        {!isReference && showViewCount && (
          <div className={styles.vsLabel}>
            {revealResult === 'correct' ? 'Correct!' : 'Wrong!'}
          </div>
        )}
      </div>
    </div>
  );
}
