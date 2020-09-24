var socket = null;
var timer = null;
$(document).ready(function(){
    socket = io.connect(); // 3000 port 웹 서버와 연결
    // nodejs 보낸 데이터를 수신하는 부분
    // www 파일의 results[0]이 data로
    console.log('map_result received');
    socket.on("map_result_evt",function(data){
        $('.map_result').html("<img src="+data+" weight='480' height='360' alt='waiting'/>");
    });   
    if(timer == null){
        // setInterval: 1초에 한 번씩 timer1 함수를 호출하라
        timer = window.setInterval("timer1()", 1000); //1000: 1초
    }     
});
function timer1(){
    socket.emit("map_result_evt", JSON.stringify({}));
    console.log("_--___1초마다_____--_")
    console.log("______map result______")
}
