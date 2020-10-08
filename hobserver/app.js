var createError = require('http-errors');
var express = require('express');
var path = require('path');
var cookieParser = require('cookie-parser');
var logger = require('morgan');

var mainRouter = require('./routes/main');
var usersRouter = require('./routes/users');

var app = express();

// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'ejs');
app.engine('html', require('ejs').renderFile);

app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

app.get('/', function(req, res){
  res.sendFile(__dirname + '/public/hobserver.html');
});
app.use('/users', usersRouter);
app.use('/', mainRouter);
app.use('/event', express.static('./public/javascripts/event.js'));

app.io = require('socket.io')();

// mongoDB 객체를 생성하고 연결
var mongoDB = require('mongodb').MongoClient;
var url = 'mongodb://127.0.0.1:27017';
var dbObj = null;
mongoDB.connect(url, { useUnifiedTopology: true }, function(err, db){
  dbObj = db.db('Hobserver');
  console.log("hobserver db connect~");
  // 'map_origin_evt' 이벤트 등록 - map_origin.jpg 이미지 
  var socketIoImage1 = require('./modules/socketIoImage.js')(app.io, 'map_origin_evt', dbObj,'map_origin.jpg');
  // 'map_result_evt' 이벤트 등록 - map_result.jpg 이미지
  var socketIoImage2 = require('./modules/socketIoImage.js')(app.io, 'map_result_evt', dbObj,'map_result.jpg');
  // 'intruder_evt' 이벤트 등록 - intruder.jpg 이미지
  var socketIoImage3 = require('./modules/socketIoImage.js')(app.io, 'intruder_evt', dbObj,'intruder.jpg');
  // OTP 이벤트 등록
  var socketIoOTP = require('./modules/socketIoOTP.js')(app.io, dbObj, 'otp_state_evt');
});

// catch 404 and forward to error handler
app.use(function(req, res, next) {
  next(createError(404));
});

// error handler
app.use(function(err, req, res, next) {
  // set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = req.app.get('env') === 'development' ? err : {};

  // render the error page
  res.status(err.status || 500);
  res.render('error');
});

module.exports = app;
