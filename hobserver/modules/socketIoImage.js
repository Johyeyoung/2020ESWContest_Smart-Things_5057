module.exports = function(io, event, db, fileName){ 
    // io: 소켓 객체, event: 이벤트명
    // db: 데이터베이스, fileName: MongoDB에서 가져올 사진 파일 이름
    io.on('connection', function(socket){ // 'connection' 이벤트 등록
        var files_collection = db.collection('images.files');
        var chunks_collection = db.collection('images.chunks');
        // 이벤트 리스너
        socket.on(event, function(data){
            files_collection.find({filename:fileName}).toArray(function(err, docs){
                if(err){
                    console.log('files_collection find error : ' + fileName);
                } 
                if(!docs||docs.length === 0){
                    console.log('docs error : ' + fileName);
                }else{
                    // Retrieving the chunks from the db
                    chunks_collection.find({files_id:docs[0]._id}).sort({n:1}).toArray(function(err,  chunks){
                      
                        if(err){ // 에러 메시지 출력
                            console.log('chunks_collection find error : ' + fileName);
                        }
                        let fileData = [];
                        for(let i =0;i < chunks.length;i++){
                            fileData.push(chunks[i].data.toString('base64'));
                        }
                        let finalFile = 'data:image/jpeg;base64,' + fileData.join('');
                        socket.emit(event, finalFile);
                        console.log('emit image event to client and send finalFile');
                        // 다시 클라이언트에게 이벤트 전송
                    });
                }
            });
        });
    })
};