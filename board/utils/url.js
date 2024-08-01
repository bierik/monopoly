function pathJoin(...parts) {
  const sep = "/";
  return parts.join(sep).replace(new RegExp(sep + "{1,}", "g"), sep);
}

export function createPlayerURL(path) {
  const origin = new URL(window.location.origin);
  origin.pathname = pathJoin("/player", path);
  return origin.toString();
}

export function createCreateGameURL(token) {
  return createPlayerURL(`/game/create/${toValue(token)}`);
}

export function createJoinGameURL(gameId) {
  return createPlayerURL(`/game/${toValue(gameId)}/join`);
}
