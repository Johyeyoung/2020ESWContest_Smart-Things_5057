var socket = null;
var timer = null;
$(document).ready(function(){
    socket = io.connect(); // 3000 port 웹 서버와 연결함
    // nodejs 보낸 데이터를 수신하는 부분
    console.log('map_origin received');
    // 'map_origin_evt' 이벤트 수신 시 html 출력
    var img_size = ' width="300" height="300" style="margin-top:-36px;"/>';
    socket.on("map_origin_evt",function(data){
        $('.map_origin').html('<div class="blinking"> 객체가 발견되었습니다</div><br>'
        +'<img src='+ data + img_size);
    });
    console.log('map_result received');
    socket.on("map_result_evt",function(data){
        $('state_check1').remove();
        $('.map_result').html('<div class="blinking">객체를 추적하는 중입니다</div><br>'+
        '<img src=' + data + img_size);
    });
    // 경로 갱신 시
    socket.on("map_result2_evt",function(data){
        $('state_check1').remove(); // 안되면 position 으로 덮어씌우기
        $('.map_result2').html('<div class="blinking">객체를  </div><br>'+
        '<img src=' + data + img_size);
    });
    console.log('intruder_evt received');
    socket.on("intruder_evt",function(data){
        $('.intruder').html('<div class="blinking">침입자 이미지입니다</div><br>'+ 
        '<img src=' + data + img_size);
    });
    socket.on("otp_state_evt",function(data){
        data = JSON.parse(data);
        var alarm_color=' style="color:red; margin-bottom:-20px;">';
        if(data.text ==='Success'){ // OTP 인증 성공임을 확인 알림
            $(".otpInfo").html('<div class="success" style="margin-top:-30px; margin-bottom:-20px;">' +
            'OTP 인증되었습니다</div>');
        }else if(data.text ==='Fail'){ // OTP 인증 실패임을 확인 알림
            $(".otpInfo").html('<div class="blinking"'+alarm_color + 
            'OTP 인증 실패했습니다</div>');
        }else if(data.text ==='Real Fail'){ // OTP 인증 5회 실패 시 알림
            $(".otpInfo").html('<div class="blinking"'+ alarm_color + 
            'OTP 5회 실패! 관리자 확인 요망</div>');
        }else if(data.text ==='Time_Over'){ // OTP 시간 초과 알림
            $(".otpInfo").html('<div class="blinking"'+alarm_color+
            '시간 초과입니다. 다시 추적합니다</div>');
        }        
    });       
    if(timer == null){
        // setInterval: 1초에 한 번씩 timer1 함수를 호출하여 데이터 확인
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
    socket.emit("map_result2_evt", JSON.stringify({}));
    console.log("map_result2")
    console.log("___________________")
    socket.emit("otp_state_evt", JSON.stringify({}));
    console.log("otp_state")
    console.log("___________________")
    socket.emit("intruder_evt", JSON.stringify({}));
    console.log("interuder")
    console.log("___________________")
}
