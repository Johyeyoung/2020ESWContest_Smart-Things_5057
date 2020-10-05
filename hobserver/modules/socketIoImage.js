module.exports = function(io, event, db,fileName){
    io.on('connection', function(socket){
        console.log('server!');
        var files_collection = db.collection('images.files');
        var chunks_collection = db.collection('images.chunks');
        socket.on(event, function(data){
            files_collection.find({filename:fileName}).toArray(function(err, docs){
                if(err){
                    console.log('files_collection find error : ' + fileName);
                }
                if(!docs||docs.length===0){
                    console.log('docs error : ' + fileName);
                }else{
                    //Retrieving the chunks from the db
                    chunks_collection.find({files_id:docs[0]._id}).sort({n:1}).toArray(function(err,  chunks){
                        if(err){
                            console.log('chunks_collection find error : ' +fileName);
                        }
                        let fileData = [];
                        for(let i =0;i<chunks.length;i++){
                            fileData.push(chunks[i].data.toString('base64'));
                        }
                        let finalFile = 'data:image/jpeg;base64,' + fileData.join('');
                        console.log('emit image event to client and send finalFile');
                        socket.emit(event, finalFile);
                    });
                }
            });
        });
    })
};