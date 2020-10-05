var socket = null;
var timer = null;
$(document).ready(function(){
    socket = io.connect(); // 3000 port 웹 서버와 연결
    // nodejs 보낸 데이터를 수신하는 부분
  
    console.log('map_origin received');
    socket.on("map_origin_evt",function(data){
        if(!data){$('.map_origin').html("경로 탐색 모드가 실행됩니다.");}
        $('.map_origin').html("맵을 생성합니다..<br> <img src="+data+" weight='400' height='300' alt='waiting'/>");
        // 경로 탐색 모드가 실행됩니다
    });
    console.log('map_result received');
    socket.on("map_result_evt",function(data){
        if(!data){$('.map_result').html("객체를 추적하는 중입니다.");}
        $('.map_result').html("<br> <img src="+data+" weight='400' height='300' alt='waiting'/> ");
        
        // 객체를 추적하는 중입니다
    });
    console.log('intruder_evt received');
    socket.on("intruder_evt",function(data){
        $('.intruder').html("<br> <img src="+data+" weight='400' height='300' alt='waiting'/>");
    });
    socket.on("otp_state_evt",function(data){
        data = JSON.parse(data);
        // console.log(data);
        // $(".standby_otp").html('<span>[OTP 인증]</span>');
        // if(!data){
        //     $(".otpInfo").html('<span style="color:red">인증을 기다리고 있습니다..</span>');
        // }
        if(data.text ==='Success'){
            $(".otpInfo").html('<span class="success">OTP 인증되었습니다</span>');
        }else if(data.text ==='Fail'){
            $(".otpInfo").html('<span class="blinking">OTP 인증 실패했습니다</span>');
        }else if(data.text ==='Real Fail'){
            $(".otpInfo").html('<span class="blinking">OTP 5회 실패! 관리자 확인 요망</span>');
        }          
    });       
    if(timer == null){
        // setInterval: 1초에 한 번씩 timer1 함수를 호출하라
        timer = window.setInterval("timer1()", 3000); //1000: 1초
    }        
      
});
function timer1(){
    socket.emit("map_origin_evt", JSON.stringify({}));
    console.log("map origin")
    console.log("___________________")
    socket.emit("map_result_evt", JSON.stringify({}));
    console.log("map_result")
    console.log("___________________")
    socket.emit("otp_state_evt", JSON.stringify({}));
    console.log("otp_state")
    console.log("___________________")
    socket.emit("intruder_evt", JSON.stringify({}));
    console.log("interuder")
    console.log("___________________")
}
