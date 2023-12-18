import mqtt from 'mqtt'

const topicHandlers = new Map()
const client = await mqtt.connectAsync('mqtt://localhost:5001')

client.on('message', (topic, message) => {
  const handlers = topicHandlers.get(topic) || []
  handlers.forEach((handler) => handler(JSON.parse(message.toString())))
})

export const useSubscribe = () => (topic) => {
  return client.subscribeAsync(topic)
}

export const useOnMessage = () => (topic, callback) => {
  const handlers = topicHandlers.get(topic) || []
  topicHandlers.set(topic, [...handlers, callback])
}
