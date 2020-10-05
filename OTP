#include <iom128v.h>
void delay_ms(unsigned int ms);
void LCD_pos(unsigned char col, unsigned char row);
void write_str(unsigned char *str);
void write_data(char data); void write_instruction(char i_data);
void init_LCD(void);
void timer_init(void);
int intselect=0, timer=0, sec=0;
unsigned char exchange=0, tslect=0;
unsigned char t=0;
unsigned long int x, sn, time, p, y, p2, in;


#pragma interrupt_handler timer0_comp_isr:iv_TIM0_COMP//타이머 인터럽트
void timer0_comp_isr(void)
{
        timer++;
        if(timer==124)
        {
            timer=0;
            sec++;
        }
}
#pragma interrupt_handler int0_isr:iv_INT0 // OTP숫자 입력
void int0_isr(void)
{
    intselect=1;
}

#pragma interrupt_handler int1_isr:iv_INT1 //자리수 변경
void int1_isr(void)
{
    intselect=2;
}

#pragma interrupt_handler int2_isr:iv_INT2 //OTP 비교 결과 출력
void int2_isr(void)
{
    intselect=3;
}

#pragma interrupt_handler int4_isr:iv_INT4 //시계 설정
void int4_isr(void)
{
    intselect=4;
}

#pragma interrupt_handler int5_isr:iv_INT5 //시계 설정2
void int5_isr(void)
{
    intselect=5;
}
#pragma interrupt_handler int6_isr:iv_INT6 //입력 초기화
void int6_isr(void)
{
    intselect=6;
}

void timer_init(void)
{
    TCCR0 = 0x1F;
    OCR0=125;
    TIMSK=0x02;
}

void interrupt_init (void)
{
    EICRA=0xaa;  // INT0~2- 하강 에지 트리거
    EICRB=0xaa;  //INT4 하강 에지 트리거
    EIMSK = 0xff;  // INT0~2,4 허용
    SREG = 0x80; // Global interrupt 허용
    DDRD = 0x00; // input 으로 설정
    DDRE = 0x00; // input 으로 설정
    PORTD = 0Xff; //INT0~3 - 내부 pull up 사용
    PORTE = 0Xff;
}
void delay_ms(unsigned int m)
{
    unsigned int i, j;
    for(i=0;i<m;i++)
    {
        for(j=0;j<2100;j++);
    }
}

void LCD_pos(unsigned char row, unsigned char col)
{
    write_instruction(0x80 | (row*0x40+col));
}
void write_str(unsigned char *str)
{
    while(*str != 0)
    {
        write_data(*str);
        str++;
    }
}
void write_data(char data)
{
    PORTB = 0xA0;
    PORTC = data;
    delay_ms(1);
    PORTB = 0x00;
}
void write_instruction(char i_data)
{
    PORTB = 0x80;
    PORTC = i_data;
    delay_ms(2);
    PORTB = 0x00;
}
void init_LCD(void)
{
    write_instruction(0x3c);
    write_instruction(0x01);
    write_instruction(0x06);
    write_instruction(0x0c);
}

void main(void)
{
    timer_init();
    interrupt_init();
    unsigned char onetime=0;
    unsigned char str2[] = ":";
    unsigned char str3[] = " OK!   ";
    unsigned char str4[] = "FAIL!  ";
    unsigned char str8[] = "TIME";
    unsigned char str9[] = "OTP";
    unsigned char str10[] = "WAITING";
    int min=0, hour=0, k=0, wait=0;
    int pw=0, p1=0, p3=0, p4=0, p5=0, p6=0, s=0;
    unsigned long int n[2];
    sec = 0;
    min = 55;
    hour = 15;
    x = 257465;  // 초기 otp시드 6자리
    sn = 2576451; // 시리얼넘버 7자리
    p=6591; // 사용자 패스워드 6571
    exchange = 0;
    pw = 0;
    k=0;
    time = 0;
    DDRB = 0xff; //출력
    DDRC = 0xff; //출력
    DDRA = 0xff; //출력
    n[1]=1111111;
    init_LCD();

    while(1)
    {

        ///시간 계산
         if(sec>=60)
        {
            sec=0;
            min++;
        }
        if(min>=60)
        {
            min=0;
            hour++;
        }
        if(hour>=24)
        {
            hour = 0;
        }


        ///OTP계산
        if(onetime==0)
        {
            if(sec==0||sec==20||sec==40)    //20마다 생성
           {
                time = (sec*100000 + min * 1000 + hour * 10) + sec; //시간값 변환
                if(time<1000000)
                {
                    time = time + sn;
                }
                y = p*x;            //OTP계산
                if(y<10000000)
                {
                    y = y+10000000;
                }
                x = (y+sn)%time;    //OTP 계산
                if(x>999999)
                {
                    x = x%1000000;
                }

                p1=0,p2=0,p3=0,p4=0,p5=0,p6=0;

                n[k]=x;
                k++;
                if(k==2) k=0;
                onetime=~onetime;

            }
        }
        if(onetime!=0)
        {
            if(sec==1||sec==21||sec==41) onetime=~onetime;
        }


            if(exchange==0)
            {

                LCD_pos(1,0);
                write_str(str9);   //'OTP'
                if(wait == 0)
                {
                    LCD_pos(1,5);
                    write_str(str10);   //'WAITING'
                }
                else
                {
                    LCD_pos(1,5);
                    write_data(p1+'0');
                    write_data(p2+'0');
                    write_data(p3+'0');
                    write_data(p4+'0');
                    write_data(p5+'0');
                    write_data(p6+'0');
                    write_data(' ');
                    LCD_pos(1,13);
                    write_data('[');
                    write_data(s+'1');
                    write_data(']');
                }
            }

            else if(exchange!=0)
            {
                ///입력한 OTP
                in=p1*100000+p2*10000+p3*1000+p4*100+p5*10+p6;
                ///비교
                if(in==n[1]||in==n[0])   //맞으면
                {
                    LCD_pos(1,5);
                    write_str(str3);    //OK!
                    PORTA=0x04;
                    delay_ms(500);
                }

                else  //틀리면
                {
                    LCD_pos(1,5);
                    write_str(str4);   //FAIL!
                    PORTA=0x02;
                    delay_ms(500);
                }
                PORTA=0x00;
                exchange = 0;
            }
                LCD_pos(0,0);
                write_str(str8);   //'TIME'
                LCD_pos(0,5);
                write_data((hour/10)+'0');
                write_data((hour%10)+'0');
                write_str(str2);    //:'
                LCD_pos(0,8);
                write_data((min/10)+'0');
                write_data((min%10)+'0');
                write_str(str2);
                LCD_pos(0,11);
                write_data((sec/10)+'0');
                write_data((sec%10)+'0');


            ///인터럽트 대체
            if(intselect==0)
            {
                //아무것도 안함
            }
            //int0
            else if(intselect==1)
            {
                pw++; // 수 1씩증가
                if(pw==10) pw=0;
                if(s==0)
                {
                    p1= pw;
                    if(p1==10) p1=0;
                }  // 자릿수가 0일때 첫번째 자리 p1에 저장
                else if(s==1)
                {
                    p2= pw;
                    if(p2==10) p2=0;
                }  // 자릿수가 1일때 첫번째 자리 p2에 저장
                else if(s==2)
                {
                    p3= pw;
                    if(p3==10) p3=0;
                }  // 자릿수가 1일때 첫번째 자리 p2에 저장 // 자릿수가 2일때 첫번째 자리 p3에 저장
                else if(s==3)
                {
                    p4= pw;
                    if(p4==10) p4=0;
                }  // 자릿수가 1일때 첫번째 자리 p2에 저장 // 자릿수가 3일때 첫번째 자리 p4에 저장
                else if(s==4)
                {
                    p5= pw;
                if(p5==10) p5=0;
                }  // 자릿수가 1일때 첫번째 자리 p2에 저장 p5= pw; // 자릿수가 4일때 첫번째 자리 p5에 저장
                else if(s==5)
                {
                    p6= pw;
                if(p6==10) p6=0;
                }  // 자릿수가 1일때 첫번째 자리 p2에 저장 p6= pw; // 자릿수가 5일때 첫번째 자리 p6에 저장
                ///채터링 제거 코드
                delay_ms(10);
                while(~PIND&0x01) ;
                delay_ms(10);
                EIFR = (1<<INTF0);
                intselect=0;
            }
            //int1
            else if(intselect==2)
            {
                s++; // 자릿수(오른쪽으로 1씩) 증가
                pw=0; // 0으로 초기화
                if(s==6) s=0; // 6번째 자릿수 후에 첫번쨰 자리수 초기화
                ///채터링 제거 코드
                delay_ms(10);
                while(~PIND&0x02) ;
                delay_ms(10);
                EIFR = (1<<INTF1);
                intselect=0;
            }
            //int2
            else if(intselect==3)
            {
                if(exchange!=0) //승인 하고 나서 화면 전환
                {
                    if(in==n[1])
                    {
                        n[1]=1111111;
                    }
                    else if(in==n[0])
                    {
                        n[0]=1111111;
                    }
                }
                exchange=~exchange;

                ///채터링 제거 코드
                delay_ms(10);
                while(~PIND&0x04) ;
                delay_ms(10);
                EIFR = (1<<INTF2);
                intselect=0;
            }
            //int4
            else if(intselect==4)
            {
                    wait = ~wait;
                    ///채터링 제거 코드
                    delay_ms(10);
                    while(~PINE&0x10) ;
                    delay_ms(10);
                    EIFR = (1<<INTF4);
                    intselect=0;
            }

    }
}
