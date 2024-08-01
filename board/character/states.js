import { State } from "yuka";
export const STATES = {
  IDLE: "IDLE",
  RUN: "RUN",
  WALK: "WALK",
};

export class IdleState extends State {
  enter(character) {
    character.actions.get("Idle").reset().fadeIn(1);
  }

  execute(character) {
    if (character.getSpeed() >= 1) {
      character.stateMachine.changeTo(STATES.WALK);
    }
  }

  exit(character) {
    character.actions.get("Idle").reset().fadeOut(1);
  }
}

export class WalkState extends State {
  enter(character) {
    character.actions.get("Walk").reset().fadeIn(1);
  }

  execute(character) {
    if (character.getSpeed() >= 8) {
      character.stateMachine.changeTo(STATES.RUN);
    }
    if (character.getSpeed() < 1) {
      character.stateMachine.changeTo(STATES.IDLE);
    }
  }

  exit(character) {
    character.actions.get("Walk").reset().fadeOut(1);
  }
}

export class RunState extends State {
  enter(character) {
    character.actions.get("Run").reset().fadeIn(1);
  }

  execute(character) {
    if (character.getSpeed() < 8) {
      character.stateMachine.changeTo(STATES.WALK);
    }
  }

  exit(character) {
    character.actions.get("Run").reset().fadeOut(1);
  }
}
