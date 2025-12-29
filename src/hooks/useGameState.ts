import { useReducer, useCallback, useMemo } from 'react';
import type { Meme, GameState, GameAction } from '../types';
import { getRandomMeme, getRandomMemePair } from '../utils/shuffleMemes';

const initialState: GameState = {
  phase: 'start',
  currentMeme: null,
  comparisonMeme: null,
  currentStreak: 0,
  highScore: 0,
  usedMemeIds: new Set(),
  lastGuessCorrect: null,
};

function gameReducer(state: GameState, action: GameAction): GameState {
  switch (action.type) {
    case 'START_GAME':
      return {
        ...state,
        phase: 'playing',
        currentMeme: action.payload.currentMeme,
        comparisonMeme: action.payload.comparisonMeme,
        currentStreak: 0,
        usedMemeIds: new Set([action.payload.currentMeme.id, action.payload.comparisonMeme.id]),
        lastGuessCorrect: null,
      };

    case 'GUESS':
      return {
        ...state,
        phase: 'revealing',
      };

    case 'REVEAL_RESULT':
      return {
        ...state,
        lastGuessCorrect: action.payload.isCorrect,
        currentStreak: action.payload.isCorrect ? state.currentStreak + 1 : state.currentStreak,
      };

    case 'NEXT_ROUND':
      return {
        ...state,
        phase: 'playing',
        currentMeme: state.comparisonMeme,
        comparisonMeme: action.payload.newMeme,
        usedMemeIds: new Set([...state.usedMemeIds, action.payload.newMeme.id]),
        lastGuessCorrect: null,
      };

    case 'GAME_OVER':
      return {
        ...state,
        phase: 'gameover',
      };

    case 'RESET':
      return {
        ...initialState,
        highScore: state.highScore,
      };

    default:
      return state;
  }
}

export function useGameState(memes: Meme[], externalHighScore: number) {
  const [state, dispatch] = useReducer(gameReducer, {
    ...initialState,
    highScore: externalHighScore,
  });

  // Update high score when external value changes
  const stateWithHighScore = useMemo(() => ({
    ...state,
    highScore: Math.max(state.highScore, externalHighScore),
  }), [state, externalHighScore]);

  const startGame = useCallback(() => {
    const pair = getRandomMemePair(memes, new Set());
    if (pair) {
      dispatch({
        type: 'START_GAME',
        payload: { currentMeme: pair[0], comparisonMeme: pair[1] },
      });
    }
  }, [memes]);

  const makeGuess = useCallback((guess: 'higher' | 'lower') => {
    if (!state.currentMeme || !state.comparisonMeme) return;

    dispatch({ type: 'GUESS', payload: { guess } });

    const currentViews = state.currentMeme.views;
    const comparisonViews = state.comparisonMeme.views;

    let isCorrect: boolean;
    if (guess === 'higher') {
      isCorrect = comparisonViews >= currentViews;
    } else {
      isCorrect = comparisonViews <= currentViews;
    }

    // Reveal result after a short delay
    setTimeout(() => {
      dispatch({ type: 'REVEAL_RESULT', payload: { isCorrect } });

      // After revealing, either continue or end game
      setTimeout(() => {
        if (isCorrect) {
          // Get next meme, potentially resetting pool if needed
          let usedIds = state.usedMemeIds;
          if (usedIds.size >= memes.length - 1) {
            // Keep current comparison meme, reset the rest
            usedIds = new Set([state.comparisonMeme!.id]);
          }

          const newMeme = getRandomMeme(memes, new Set([...usedIds, state.comparisonMeme!.id]));
          if (newMeme) {
            dispatch({ type: 'NEXT_ROUND', payload: { newMeme } });
          } else {
            // Fallback: get any meme that's not the current comparison
            const fallback = getRandomMeme(memes, new Set([state.comparisonMeme!.id]));
            if (fallback) {
              dispatch({ type: 'NEXT_ROUND', payload: { newMeme: fallback } });
            }
          }
        } else {
          dispatch({ type: 'GAME_OVER' });
        }
      }, 1500);
    }, 500);
  }, [state.currentMeme, state.comparisonMeme, state.usedMemeIds, memes]);

  const guessHigher = useCallback(() => makeGuess('higher'), [makeGuess]);
  const guessLower = useCallback(() => makeGuess('lower'), [makeGuess]);

  const resetGame = useCallback(() => {
    dispatch({ type: 'RESET' });
  }, []);

  const playAgain = useCallback(() => {
    resetGame();
    // Small delay to ensure reset is processed
    setTimeout(startGame, 50);
  }, [resetGame, startGame]);

  return {
    state: stateWithHighScore,
    startGame,
    guessHigher,
    guessLower,
    resetGame,
    playAgain,
  };
}
