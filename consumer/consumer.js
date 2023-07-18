const { Kafka } = require("kafkajs")
const fs = require('fs');
const { Readable } = require('stream');
const clientId = "my-app"
const brokers = ["localhost:29092"]
const topic = "motion_video"
const kafka = new Kafka({ clientId, brokers })
const consumer = kafka.consumer({ groupId: clientId })
let messages = []
let buf_array = []

const consume = async () => {
	// first, we wait for the client to connect and subscribe to the given topic
	await consumer.connect()
	await consumer.subscribe({ topic })
	await consumer.run({
		// this function is called every time the consumer gets a new message
		eachMessage: ({ message }) => {
			console.log(`received message: key: ${message.key}  -  value lenght: ${message.value.length}`)
			if (message.key == 0) {
				messages = []
				messages.push(message)
			} else if (message.key.toString() == 'end') {
				const objs = messages
				objs.sort((a, b) =>
					JSON.parse(a.key) > JSON.parse(b.key)
						? 1
						: JSON.parse(b.key) > JSON.parse(a.key)
							? -1
							: 0
				)
				messages = []
				buf_array = []
				buf_array = objs.map((b) => b.value)
				outfile = message.value
				var date = new Date();
				date.setHours(0, 0, 0, 0);
				var time = date.getTime();
				dir = `./NAS/${time}`
				if (!fs.existsSync(dir)) {
					fs.mkdirSync(dir, { recursive: true });
				}

				const videoFileReadable = new Readable();
				videoFileReadable._read = () => { };
				buf_array.forEach(chunk => {
					videoFileReadable.push(chunk);
				});
				videoFileReadable.push(null);

				const outputVideoFileStream = fs.createWriteStream(dir + '/' + outfile);
				videoFileReadable.pipe(outputVideoFileStream);
			} else {
				messages.push(message)
			}
		},
	})
}

module.exports = consume