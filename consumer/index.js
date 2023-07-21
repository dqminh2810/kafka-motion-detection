const consume = require("./consumer.js")
const cron = require("node-cron");
const fs = require('fs');

consume().catch((err) => {
	console.error("error in consumer: ", err)
})
// add cron to delete files every midnight
cron.schedule("0 0 0 * * *", function () {
	console.log("---------------------Start remove in day video recording---------------------");
	dir = `./NAS/`
	fs.rmSync(dir, { recursive: true, force: true });
	console.log("---------------------End remove in day video recording---------------------");
  });