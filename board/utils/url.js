export function createPlayerURL(path) {
  return `https://player.local:8000${path}`;
}

export function createCreateGameURL(token) {
  return createPlayerURL(`/game/create/${toValue(token)}`);
}

export function createJoinGameURL(gameId) {
  return createPlayerURL(`/game/${toValue(gameId)}/join`);
}
