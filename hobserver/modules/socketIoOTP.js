module.exports = function(io, db, event){
    // io: 소켓 객체, db: 데이터베이스, event: 이벤트 명
    io.on('connection', function(socket){
        // 이벤트 리스너
        socket.on(event, function(data){
            console.log('connect socket - otp event')
            var otp_value = db.collection('otp_result');
            // 'otp_result' 컬렉션에서 가장 최근의 값을 찾는다
            otp_value.find({}).sort({_id:-1}).limit(1).toArray(function(err, results){
            // 에러가 아니면 results 의 데이터들을 hobserver.html 로 보냄
            // socket을 통해 3000포트로 이벤트("otp_state_evt")와 데이터(JSON.stringify(results[0]))를 보낸다.
            // JSON 으로 emit(보냄)
            // console.log(results[0]);
                if(!err){
                    console.log('otp state emit to client!');
                    socket.emit(event, JSON.stringify(results[0]));
                }
            });
        });
    })
};
