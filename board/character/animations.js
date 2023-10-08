export function actionFromMixer(mixer, actionName) {
  const action = mixer.clipAction(actionName);
  action.play();
  action.enabled = false;
  return action;
}

export function actionsFromMixer(mixer, actions = []) {
  const actionsMap = new Map();
  actions.forEach((action) => {
    actionsMap.set(action, actionFromMixer(mixer, action));
  });
  return actionsMap;
}
