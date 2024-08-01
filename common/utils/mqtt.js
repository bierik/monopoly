import mqtt from "mqtt";

const topicHandlers = new Map();

function getConnectionURL() {
  const url = new URL(window.location.origin);
  url.protocol = window.location.protocol.endsWith("s:") ? "wss" : "ws";
  url.pathname = "mqtt";
  return url.toString();
}
const client = await mqtt.connectAsync(getConnectionURL());

client.on("message", (topic, message) => {
  const handlers = topicHandlers.get(topic) || [];
  handlers.forEach((handler) => handler(JSON.parse(message.toString())));
});

await client.subscribeAsync("+/game/created");
await client.subscribeAsync("game/+/changed");
await client.subscribeAsync("game/+/moved");
await client.subscribeAsync("participation/created");
await client.subscribeAsync("participation/+/changed");

function removeMessageHandler(topic) {
  topicHandlers.delete(topic);
}

function addMessageHandler(topic, callback) {
  const handlers = topicHandlers.get(topic) || [];
  topicHandlers.set(topic, [...handlers, callback]);
}

export function onMessage(topic, callback) {
  watch(
    toRef(topic),
    (newTopic, oldTopic) => {
      removeMessageHandler(toValue(oldTopic));
      addMessageHandler(toValue(newTopic), callback);
    },
    {
      immediate: true,
    }
  );
}
