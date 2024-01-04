import mqtt from 'mqtt'

const topicHandlers = new Map()
const client = await mqtt.connectAsync('mqtt://localhost:5001')

client.on('message', (topic, message) => {
  const handlers = topicHandlers.get(topic) || []
  handlers.forEach((handler) => handler(JSON.parse(message.toString())))
})

await client.subscribeAsync('game/+/started')

export const useSubscribe = () => (topic) => {
  return client.subscribeAsync(topic)
}

function removeMessageHandler(topic) {
  topicHandlers.delete(topic)
}

function addMessageHandler(topic, callback) {
  const handlers = topicHandlers.get(topic) || []
  topicHandlers.set(topic, [...handlers, callback])
}

export const useOnMessage = () => (topic, callback) => {
  watch(
    topic,
    (newTopic, oldTopic) => {
      removeMessageHandler(toValue(oldTopic))
      addMessageHandler(toValue(newTopic), callback)
    },
    {
      immediate: true,
    },
  )
}
