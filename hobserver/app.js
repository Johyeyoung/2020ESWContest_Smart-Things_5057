var createError = require('http-errors');
var express = require('express');
var path = require('path');
var cookieParser = require('cookie-parser');
var logger = require('morgan');

var indexRouter = require('./routes/index');
var usersRouter = require('./routes/users');

var app = express();

// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'jade');

app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));


// app.use('/', indexRouter);
app.get('/', function(req, res){
  res.sendFile(__dirname+'/public/hobserver.html');
});
app.use('/users', usersRouter);
app.use('/event', express.static('./public/javascripts/event.js'));

app.io = require('socket.io')();
// socket.io 의 이벤트 등록 및 위의 socket.io 라이브러리르 socketIoHandler에게 전달

var mongoDB = require('mongodb').MongoClient;
var url = 'mongodb://127.0.0.1:27017';
var dbObj = null;
mongoDB.connect(url, { useUnifiedTopology: true }, function(err, db){
  dbObj = db.db('Hobserver');
  console.log("hobserver db connect~");
  var socketIoImage1 = require('./modules/socketIoImage.js')(app.io, 'map_origin_evt',dbObj,'map_origin.jpg');
  var socketIoImage2 = require('./modules/socketIoImage.js')(app.io, 'map_result_evt', dbObj,'map_result.jpg');
  var socketIoImage3 = require('./modules/socketIoImage.js')(app.io, 'intruder_evt', dbObj,'intruder.jpg');
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
