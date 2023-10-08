<template>
  <QrcodeStream
    :track="paintOutline"
    @detect="detected"
    @camera-on="loading = false"
  >
    <div v-if="loading" class="flex size-full items-center justify-center">
      <span class="loading loading-ring loading-lg" />
    </div>
  </QrcodeStream>
</template>
<script setup>
import { first } from "lodash-es";

const loading = ref(true);
const router = useRouter();
const { color, width } = defineProps({
  color: {
    type: String,
    default: () => "green",
  },
  width: {
    type: Number,
    default: () => 8,
  },
});

function paintOutline(detectedCodes, ctx) {
  const detectedCode = first(detectedCodes);
  const [firstPoint, ...otherPoints] = detectedCode.cornerPoints;

  ctx.strokeStyle = color;
  ctx.lineWidth = width;

  ctx.beginPath();
  ctx.moveTo(firstPoint.x, firstPoint.y);
  otherPoints.forEach(({ x, y }) => {
    ctx.lineTo(x, y);
  });
  ctx.lineTo(firstPoint.x, firstPoint.y);
  ctx.closePath();
  ctx.stroke();
}

const joinPattern = /^\/game\/(?<gameId>\d.)\/join$/;
const newPattern = /^\/game\/create\/(?<token>.{36})$/;

function isJoin(path) {
  return joinPattern.test(path);
}

function isNew(path) {
  return newPattern.test(path);
}

function extractGameId(path) {
  return path.match(joinPattern).groups.gameId;
}

function extractToken(path) {
  return path.match(newPattern).groups.token;
}

function detected(detectedCodes) {
  const path = new URL(first(detectedCodes).rawValue).pathname;
  if (isJoin(path)) {
    router.push({ name: "game-id-join", params: { id: extractGameId(path) } });
  } else if (isNew(path)) {
    router.push({
      name: "game-create-token",
      params: { token: extractToken(path) },
    });
  }
}
</script>
