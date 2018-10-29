const assert = require('assert');

const MLBFilter = require("multi-level-bloom-filter-js");
const LineByLine = require("n-readlines");

const REVOKED = 524;
const UNREVOKED = 342016;
const FP_RATE = 0.5;
const FP1_RATE = REVOKED * Math.sqrt(FP_RATE) / UNREVOKED;
const REVOKED_FILENAME = '../final_revoked.json';
const UNREVOKED_FILENAME = '../final_unrevoked.json';

var cnt = 0;
let revoked  = []
let liner = new LineByLine(REVOKED_FILENAME);
let line;
while (line = liner.next()) {
  cnt += 1;
  line = line.toString();
  revoked.push(line);
  if (cnt == REVOKED) {
    break;
  }
}

var cnt = 0;
let unrevoked = []
liner = new LineByLine(UNREVOKED_FILENAME);
while (line = liner.next()) {
  cnt += 1;
  line = line.toString();
  unrevoked.push(line);
  if (cnt == UNREVOKED) {
    break;
  }
}

var start = new Date()
let mlbf = new MLBFilter(REVOKED, UNREVOKED, revoked, unrevoked, FP_RATE, FP1_RATE);
console.log(mlbf.toJSON());
var end = new Date() - start
console.info('Build MLBFilter time: %dms', end)

var start = new Date()
error = 0
revoked.forEach(function(x){
  // contains: false means in S, true means in R
  if (mlbf.contains(x) == false) {
    error += 1;
  }
});

unrevoked.forEach(function(x){
  if (mlbf.contains(x) == true) {
    error += 1;
  }
});

var end = new Date() - start
console.log('Error Number: %d, error rate %f', error, error/(REVOKED+UNREVOKED))
console.info('Query time: %dms', end)
