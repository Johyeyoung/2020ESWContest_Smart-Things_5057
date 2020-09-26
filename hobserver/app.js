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

var fs = require('fs');
app.get('/img_result_map', function(req,res){
  fs.readFile('./public/images/map_results/map_result.jpg', function(error, data){
    res.writeHead(200, {'Content-Type': 'text/html'});
    res.end(data);
  
  });
});

app.use('/event', express.static('./public/javascripts/event.js'));
// app.use('/map_origin', express.static('./public/javascripts/origin_imgs.js'));
// app.use('/intruder', express.static('./public/javascripts/intruder.js'));
// app.use('/map_result', express.static('./public/javascripts/map_result.js'));


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
