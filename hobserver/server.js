var express = require('express'); // ExpressJS 모듈을 추가

var app = express();

var mongojs = require('mongojs'); // MongoDB 연결 해야되니 MongoJS 모듈도 추가

var db = mongojs('genie', ['images']); // 여기서 genie는 database 이름이고 images테이블을 사용할꺼라고 선언

var bodyParser = require('body-parser'); // json 형태로 파싱할꺼니까 모듈 추가

var formidable = require('formidable'); // form 태그 데이터들을 가져오는 모듈

var fs = require('fs-extra'); // 파일을 복사하거나 디렉토리 복사하는 모듈



app.use(express.static(__dirname + '/public')); //public 폴더 안에 javascript 파일과 css파일을 모아둘 예정

app.use(bodyParser.json()); // body-parser 모듈을 사용해서 파싱 해줌

app.engine('html', require('ejs').__express);

app.set('views', __dirname + '/views'); // ejs 파일들을 저장하기 위해 경로 추가했음

app.set('view engine', 'html'); // ejs를 html로 바꿔주면 html로 파일 실행됩니다.



app.get('/', function(req, res) { // 웹에서 실행할 주소가 localhost:3000/ 이거일때를 선언

    res.render('index'); // index.ejs로 써도 되고 index만 써도 파일 실행을 해줍니다.

});



app.post('/upload',function(req,res){ 

    var name = "";

    var filePath = "";

    var form = new formidable.IncomingForm();



    form.parse(req, function(err, fields, files) {

        name = fields.name;

    });



    form.on('end', function(fields, files) {

  for (var i = 0; i < this.openedFiles.length; i++) {

  var temp_path = this.openedFiles[i].path;

            var file_name = this.openedFiles[i].name;

            var index = file_name.indexOf('/'); 

            var new_file_name = file_name.substring(index + 1);

            var new_location = 'public/resources/images/'+name+'/';

            var db_new_location = 'resources/images/'+name+'/';

            //실제 저장하는 경로와 db에 넣어주는 경로로 나눠 주었는데 나중에 편하게 불러오기 위해 따로 나눠 주었음

            filePath = db_new_location + file_name;

            fs.copy(temp_path,new_location + file_name, function(err) { // 이미지 파일 저장하는 부분임

                if (err) {

                    console.error(err);

                }

            });

  }



db.images.insert({"name":name,"filePath":filePath},function(err,doc){

//디비에 저장

});

  });

    res.redirect("/"); // http://localhost:3000/ 으로 이동!

});

app.listen(3000); //server 구동 포트 localhost:3000 여기에 쓰입니다.


console.log("Server running on port 3000");