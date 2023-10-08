import * as THREE from "three";
import * as YUKA from "yuka";
import loadModel from "@/character/models";
import { actionsFromMixer } from "@/character/animations";
import { STATES, IdleState, WalkState, RunState } from "@/character/states";

class CharacterStateMachine extends YUKA.StateMachine {
  constructor(owner) {
    super(owner);
    this.add(STATES.IDLE, new IdleState());
    this.add(STATES.WALK, new WalkState());
    this.add(STATES.RUN, new RunState());
    this.changeTo(STATES.IDLE);
  }
}

class CharacterEventDispatcher extends YUKA.EventDispatcher {
  constructor(owner) {
    super();
    this.owner = owner;
  }

  arrived() {
    this.dispatchEvent({ type: "arrived", owner: this.owner });
  }
}

export default class Character extends YUKA.Vehicle {
  constructor({ model, scale = 1, board, target = "start", identifier }) {
    super();
    this.identifier = identifier;
    this.scale = new YUKA.Vector3(scale, scale, scale);
    this.model = model;
    this.board = board;
    this.eventDispatcher = new CharacterEventDispatcher(this);
    this.standsOn = null;
    this.seekTo = null;
    this.model.matrixAutoUpdate = false;
    this.loadActions(["Idle", "Walk", "Run"]);
    this.maxSpeed = 10;
    this.placeAt(target);
    this.stateMachine = new CharacterStateMachine(this);
    this.setRenderComponent(this.model, () => {
      this.model.matrix.copy(this.worldMatrix);
    });
  }

  loadActions(actions = []) {
    this.mixer = new THREE.AnimationMixer(this.model);
    this.actions = actionsFromMixer(this.mixer, actions);
  }

  update(delta) {
    super.update(delta);
    this.mixer.update(delta);
    this.stateMachine.update();
    this.updateArrive();
  }

  pathTo(target) {
    const path = this.board.buildPath(this.standsOn.name, target.name);
    const yukaPath = new YUKA.Path();
    path.forEach((node) => {
      yukaPath.add(this.board.tileForName(node).toYUKAVector());
    });
    const freeTargetSpot = target.occupySpot(this);
    yukaPath.add(
      new YUKA.Vector3(freeTargetSpot.x, freeTargetSpot.y, freeTargetSpot.z),
    );
    return yukaPath;
  }

  applyTargetSteering(target) {
    this.followPathBehavior = new YUKA.FollowPathBehavior(
      this.pathTo(target),
      10,
    );
    this.steering.add(this.followPathBehavior);
  }

  async goTo(target) {
    if (this.standsOn) {
      this.standsOn.freeSpot(this);
    }
    const targetTile = this.board.tileForName(target);
    this.seekTo = targetTile;
    this.applyTargetSteering(targetTile);
  }

  isOnTheWay() {
    return !this.standsOn.isEqual(this.seekTo);
  }

  arrive() {
    this.standsOn = this.seekTo;
    this.steering.remove(this.followPathBehavior);
    this.velocity.set(0, 0, 0);
    this.eventDispatcher.arrived();
  }

  updateArrive() {
    if (this.isOnTheWay()) {
      const distanceToSeekTo = this.seekTo
        .getSpotForCharacter(this)
        .distanceTo(this.position);
      if (distanceToSeekTo <= 0.3) {
        this.arrive();
      }
    }
  }

  placeAt(target) {
    if (this.standsOn) {
      this.standsOn.freeSpot(this);
    }
    const tile = this.board.tileForName(target);
    this.standsOn = tile;
    this.seekTo = tile;
    const freeSpot = tile.occupySpot(this);
    this.position.copy(freeSpot);
  }

  static async fromModel({ model, ...args }) {
    const { scene, animations } = await loadModel(model);

    scene.animations = animations;
    return new Character({ model: scene, ...args });
  }
}
