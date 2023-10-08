import { trimStart } from "lodash-es";

export function createPlayerURL(path) {
  return "http://localhost:5005/" + trimStart(path, "/");
}

export function createCreateGameURL(token) {
  return createPlayerURL(`/game/create/${toValue(token)}`);
}

export function createJoinGameURL(gameId) {
  return createPlayerURL(`/game/${toValue(gameId)}/join`);
}
