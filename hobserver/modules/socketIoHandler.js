exports=module.exports=function(io){
    // mongoDB 연결
    var mongodb = require('mongodb');
    var mongoDB = require('mongodb').MongoClient;
    var url = 'mongodb://127.0.0.1:27017';
    var fs = require('fs');
    var dbObj = null;
    var otp_db = null;
    mongoDB.connect(url, { useUnifiedTopology: true }, function(err, db){
    dbObj = db.db('Hobserver');
    console.log("hobserver db connect~");
    // var bucket = new mongodb.GridFSBucket(dbObj, {
    //   chunkSizeBytes:1024,
    //   bucketName:'images'
    // });
    });
    io.on('connection', function(socket){
        console.log('server!');
        socket.on('map_origin_evt', function(data){
            var files_collection = dbObj.collection('images.files');
            var chunks_collection = dbObj.collection('images.chunks');
            files_collection.find({filename:'map_origin.jpg'}).toArray(function(err, docs){
                if(err){
                    console.log('error1 !');
                }
                if(!docs||docs.length===0){
                    console.log('map origin found');
                }else{
                    //Retrieving the chunks from the db
                    chunks_collection.find({files_id:docs[0]._id}).sort({n:1}).toArray(function(err,  chunks){
                        if(err){
                            console.log('error3');
                        }
                        let fileData = [];
                        for(let i =0;i<chunks.length;i++){
                            fileData.push(chunks[i].data.toString('base64'));
                        }
                        let finalFile = 'data:image/jpeg;base64,'+fileData.join('');
                        console.log('emit map_origin to client and send finalFile');
                        socket.emit('map_origin_evt', finalFile);
                    });
                }
            });
        });
        socket.on('map_result_evt', function(data){
            var files_collection = dbObj.collection('images.files');
            var chunks_collection = dbObj.collection('images.chunks');
            files_collection.find({filename:'map_result.jpg'}).toArray(function(err, docs){
                if(err){
                    console.log('error1 !');
                }
                if(!docs||docs.length===0){
                    console.log('no map_result file found');
                }else{
                    //Retrieving the chunks from the db
                    chunks_collection.find({files_id:docs[0]._id}).sort({n:1}).toArray(function(err,  chunks){
                        if(err){
                            console.log('error3');
                        }
                        let fileData = [];
                        for(let i =0;i<chunks.length;i++){
                            fileData.push(chunks[i].data.toString('base64'));
                        }
                        let finalFile = 'data:image/jpeg;base64,'+fileData.join('');
                        console.log('emit map_origin to client ');
                        socket.emit('map_result_evt', finalFile);
                    });
                }
            });
            
        });
        socket.on('intruder_evt', function(data){
            var files_collection = dbObj.collection('images.files');
            var chunks_collection = dbObj.collection('images.chunks');
            files_collection.find({filename:'intruder.jpg'}).toArray(function(err, docs){
                if(err){
                    console.log('error1 !');
                }
                if(!docs||docs.length===0){
                    console.log('no intruder file found');
                }else{
                    //Retrieving the chunks from the db
                    chunks_collection.find({files_id:docs[0]._id}).sort({n:1}).toArray(function(err,  chunks){
                        if(err){
                            console.log('error3');
                        }
                        let fileData = [];
                        for(let i =0;i<chunks.length;i++){
                            fileData.push(chunks[i].data.toString('base64'));
                        }
                        let finalFile = 'data:image/jpeg;base64,'+fileData.join('');
                        console.log('emit intruder_evt to client and send finalFile');
                        socket.emit('intruder_evt', finalFile);
                    });
                }
            });
            
        });
        socket.on("otp_state_evt", function(data){
        
            console.log('connect socket - otp event')
            //
            var otp_value = dbObj.collection('otp_results');
        
            otp_value.find({}).sort({_id:-1}).limit(1).toArray(function(err, results){
            // 에러가 아니면 results 의 데이터들을 hobserver.html 로 보냄
            // socket을 통해 3000포트로 이벤트("otp_state_evt")와 데이터(JSON.stringify(results[0]))를 보낸다.
            // JSON 으로 emit(보내다)
            // console.log(results[0]);
                if(!err){
                    console.log('otp state emit to client!');
                    socket.emit("otp_state_evt", JSON.stringify(results[0]));
                }
            });
            
        });
    })
};