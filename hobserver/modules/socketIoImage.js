module.exports = function(io, event, db,fileName){
    // var mongoDB = require('mongodb').MongoClient;
    // var url = 'mongodb://127.0.0.1:27017';
    // var dbObj = null;
    // mongoDB.connect(url, { useUnifiedTopology: true }, function(err, db){
    //     dbObj = db.db('Hobserver');
    //     console.log("hobserver db connect~");
    // });
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