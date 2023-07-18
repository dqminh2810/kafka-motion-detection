const consume = require("./consumer.js")
consume().catch((err) => {
	console.error("error in consumer: ", err)
})