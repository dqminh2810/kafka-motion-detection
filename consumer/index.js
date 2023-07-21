const consume = require("./consumer.js")
consume().catch((err) => {
	console.error("error in consumer: ", err)
})

// add cron to delete files about 1 week