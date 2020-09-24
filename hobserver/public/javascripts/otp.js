var socket = null;
var timer = null;
$(document).ready(function(){
    socket = io.connect(); // 3000 port 웹 서버와 연결
    // nodejs 보낸 데이터를 수신하는 부분
    // www 파일의 results[0]이 data로
    console.log('otp received');
    socket.on("otp_state_evt",function(data){
        data = JSON.parse(data);
        console.log(data);
        $(".standby_otp").html('<span>OTP 인증:</span>');
        if(data.text ==='Success'){
            $(".otpInfo").html('<span style="color:red">OTP 인증되었습니다</span>');
        }else if(data.text ==='Fail'){
            $(".otpInfo").html('<span style="color:red">OTP 인증실패해습니다</span>');
        }else if(data.text ==='Real Fail'){
            $(".otpInfo").html('<span style="color:red">OTP 5회 실패! 관리자 확인 요망</span>');
        }          
    });   
    if(timer == null){
        // setInterval: 1초에 한 번씩 timer1 함수를 호출하라
        timer = window.setInterval("timer1()", 3000); //1000: 1초
    }     
});
function timer1(){
    socket.emit("otp_state_evt", JSON.stringify({}));
    console.log("_--_--_")
}
function hexToBase64(str) {
    return btoa(String.fromCharCode.apply(null, str.replace(/\r|\n/g, "").replace(/([\da-fA-F]{2}) ?/g, "0x$1 ").replace(/  $/, "").split(" ")));
}
