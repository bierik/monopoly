import 'styles/main.scss'
import Phaser, { Game } from 'phaser'
import DebugGrid from 'images/monopoly_field.jpg'
import PhaserDude from 'images/phaser-dude.png'

const config = {
  type: Phaser.AUTO,
  width: window.innerWidth,
  height: window.innerHeight,
  physics: {
    default: 'arcade',
  },
  scene: {
    preload,
    create,
    // update,
  },
}

const game = new Game(config)

function preload() {
  this.load.image('background', DebugGrid)
  this.load.image('player', PhaserDude)
}

function create() {
  this.add.image(0, 0, 'background').setOrigin(0, 0)
  this.player = this.physics.add.image(70, 890, 'player')
  this.cameras.main.startFollow(this.player, true, 0.05, 0.05)

  const left = this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.LEFT)
  const right = this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.RIGHT)
  const up = this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.UP)
  const down = this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.DOWN)

  left.on('up', () => {
    this.tweens.add({
      targets: this.player,
      x: this.player.x - 100,
      duration: 250,
    })
  })
  right.on('up', () => {
    this.tweens.add({
      targets: this.player,
      x: this.player.x + 100,
      duration: 250,
    })
  })
  up.on('up', () => {
    this.tweens.add({
      targets: this.player,
      y: this.player.y - 100,
      duration: 250,
    })
  })
  down.on('up', () => {
    this.tweens.add({
      targets: this.player,
      y: this.player.y + 100,
      duration: 250,
    })
  })
}

window.addEventListener('resize', () => {
  game.scale.resize(window.innerWidth, window.innerHeight)
})
