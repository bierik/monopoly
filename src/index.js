import 'styles/main.scss'
import Paho from 'paho-mqtt'

const client = new Paho.Client('localhost', 9001, Date.now().toString())

client.connect({ onSuccess: onConnect })
client.onMessageArrived = onMessageArrived

function onConnect() {
  client.subscribe('topic')
}

function onMessageArrived(message) {
  console.log(message.payloadString)
}
