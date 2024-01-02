<template>
  <QrcodeStream :track="paintOutline" @detect="detected" @camera-on="loading = false">
    <div class="w-full h-full flex items-center justify-center" v-if="loading">
      <span class="loading loading-ring loading-lg" />
    </div>
  </QrcodeStream>
</template>
<script setup>
const loading = ref(true)
const emit = defineEmits(['join', 'new'])
const { color, width } = defineProps({
  color: {
    type: String,
    default: () => 'green',
  },
  width: {
    type: Number,
    default: () => 8,
  },
})

function paintOutline(detectedCodes, ctx) {
  const detectedCode = detectedCodes[0]
  const [firstPoint, ...otherPoints] = detectedCode.cornerPoints

  ctx.strokeStyle = color
  ctx.lineWidth = width

  ctx.beginPath()
  ctx.moveTo(firstPoint.x, firstPoint.y)
  otherPoints.forEach(({ x, y }) => {
    ctx.lineTo(x, y)
  })
  ctx.lineTo(firstPoint.x, firstPoint.y)
  ctx.closePath()
  ctx.stroke()
}

const joinPattern = /^\/game\/(?<gameId>\d.)\/join$/
const newPattern = /^\/game\/create\/(?<token>.{36})$/

function isJoin(path) {
  return joinPattern.test(path)
}

function isNew(path) {
  return newPattern.test(path)
}

function extractGameId(path) {
  return path.match(joinPattern).groups.gameId
}

function extractToken(path) {
  return path.match(newPattern).groups.token
}

function detected(detectedCodes) {
  const path = new URL(detectedCodes[0].rawValue).pathname
  if (isJoin(path)) {
    emit('join', extractGameId(path))
  } else if (isNew(path)) {
    emit('new', extractToken(path))
  }
}
</script>
