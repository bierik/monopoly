import mqttClient from 'mqtt'

export default {
  client: null,
  topicHandlers: new Map(),
  async connect(url) {
    this.client = await mqttClient.connectAsync(url)
    this.client.on('message', (topic, message) => {
      const handlers = this.topicHandlers.get(topic) || []
      handlers.forEach((handler) => handler(JSON.parse(message.toString())))
    })
  },
  subscribe(topic) {
    return this.client.subscribeAsync(topic)
  },
  on(topic, callback) {
    const handlers = this.topicHandlers.get(topic) || []
    this.topicHandlers.set(topic, [...handlers, callback])
  },
}
