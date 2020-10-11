# Hobserver
###  - 드론과 자율주행 로봇을 이용한 항만 감시 시스템   

![image](https://user-images.githubusercontent.com/24893215/95682434-2b4ebf80-0c20-11eb-9f3c-77334a34f68f.png)

 - Embedded-Software-2020_ Smart things 부문 출품작

## 1) 프로젝트 개요

   
항만은 크기가 너무 넓어 감시하기가 까다롭고, 보안상의 허점이 많아 범죄의 표적이 되기쉽다.    
특히 밀입국과 도난사고가 잦은데, 이를 감시하기 위해서는 많은 인력과 노력이 필요하다.   
이를 극복하기 위해 우리는 항만 감시 시스템인 Hobserver를 고안하게 되었고    
이는 자동화 시스템으로써 보안과 관련해 발생하는 비용적 부담을 절감하는 효과를 가져올 것이다.


##하드웨어 구성

![image](https://user-images.githubusercontent.com/24893215/95682523-9f896300-0c20-11eb-9420-d8631554e86d.png)


## 2) How to build

 ![image](https://user-images.githubusercontent.com/24893215/95682473-5fc27b80-0c20-11eb-8b05-326d5c64cded.png)

### HW

 본 프로젝트 Hobserver에서 하드웨어는 자율주행 감시로봇(TurtleBot3), 항만Observer(CoDroneII),
 OTP 인증모듈(ATmega128)로 구성되어 있다. 하드웨어의 전체적인 구성은 다음과 같다.

 - 드론

 ![image](https://user-images.githubusercontent.com/24893215/95682602-0e66bc00-0c21-11eb-9b87-a286c36e0f6f.png)

구역마다 항만 위를 비행하며 항만을 감시하다가 객체를 탐지하면 서버로 객체의 좌표와 항만의 현장 사진을 보낸다.

 - Turtlebot

 ![image](https://user-images.githubusercontent.com/24893215/95682645-5c7bbf80-0c21-11eb-863d-ebbb09b643cc.png)

 항만의 지상에서 대기모드를 유지하고 있다가 
 서버로부터 객체의 위치 경로를 받으면
 해당 경로에 맞춰 주행해 객체를 찾고, 
 객체를 발견하면 OTP인증을 요청한다.

 - OTP 모듈(ATmega128)

 ![image](https://user-images.githubusercontent.com/24893215/95682685-94830280-0c21-11eb-815a-dd5ffe084a49.png)

 자율주행 감시 로봇에 부착되어 있으며 서버로부터 OTP인증 요청 신호를 받으면OTP인증을 실행한다. 


### SW




## 3) Member
정현성, 조혜영, 박민정, 배한빈
## 4) Deadline
참가 신청 및 개발계획서 제출 :	2020년 05월 07일 ~ 06월 08일   
본선진출팀 기술지원 교육 :	2020년 07월 ~ 09월   
본선진출팀 개발완료보고서 제출 :	2020년 09월 07일 ~ 09월 28일   
결선 :	2020년 12월 09일 ~ 12월 11일   
