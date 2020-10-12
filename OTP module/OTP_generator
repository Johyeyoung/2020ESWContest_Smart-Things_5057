#include <iom128v.h>
void delay_ms(unsigned int ms);
void LCD_pos(unsigned char col, unsigned char row);
void write_str(unsigned char *str);
void write_data(char data); void write_instruction(char i_data);
void init_LCD(void);
void timer_init(void);
int sec, timer, s;
unsigned long int x, sn, time, p, y, x2, in;
unsigned char exchange=0, tslect=0, intselect=0;


#pragma interrupt_handler timer0_comp_isr:iv_TIM0_COMP//타이머 인터럽트
void timer0_comp_isr(void)
{
        timer++;
        if(timer==125)
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



#pragma interrupt_handler int4_isr:iv_INT4 //시계 설정
void int4_isr(void)
{
    intselect=2;
}

#pragma interrupt_handler int5_isr:iv_INT5 //시계 설정2
void int5_isr(void)
{
    intselect=3;
}

void timer_init(void)
{
    TCCR0=0x1F;
    OCR0=124;
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
    unsigned char t;
    unsigned char str2[] = ":";
    unsigned char str4[] = "Press INT0";
    unsigned char str5[] = "[h]";
    unsigned char str6[] = "[m]";
    unsigned char str7[] = "[s]";
    unsigned char str8[] = "TIME";
    unsigned char str9[] = "OTP";
    unsigned long int n[2];
    int min, hour, x1, x3, x4, x5, x6, k;
    y=0;
    sec = 00;
    min = 12;
    hour = 10;
    x = 257465;  // 초기 otp시드 6자리
    sn = 2576451; // 시리얼넘버 7자리
    p=6591; // 사용자 패스워드 6571
    exchange = 0;
    t=1;
    k=0;
    time = 0;
    DDRB = 0xff; //출력
    DDRC = 0xff; //출력
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
            x1 = x/100000;
            x2 = (x%100000)/10000;
            x3 = (x%10000)/1000;
            x4 = (x%1000)/100;
            x5 = (x%100)/10;
            x6 = x%10;


        if(exchange==0) //INT0 누르기 전
        {
            LCD_pos(1,0);
            write_str(str9);   //'OTP'
            LCD_pos(1,5);
            write_str(str4);    //'Press INT0'
        }
        else if(exchange!=0)  //INT0 누르면 OTP 출력
        {
            x1 = (x%1000000)/100000;
            x2 = (x%100000)/10000;
            x3 = (x%10000)/1000;
            x4 = (x%1000)/100;
            x5 = (x%100)/10;
            x6 = x%10;

            LCD_pos(1,5);
            write_data(x1+'0');
            write_data(x2+'0');
            write_data(x3+'0');
            write_data(x4+'0');
            write_data(x5+'0');
            write_data(x6+'0');
            write_data(' ');
            write_data(' ');
            write_data(' ');
            write_data(' ');
        }
        ///시간 디스플레이
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

        if(tslect==0) write_str(str5);  //'[h]'
        if(tslect==1) write_str(str6);  //'[m]'
        if(tslect==2) write_str(str7);  //'[s]'

        if(intselect==0)
        {

        }
        else if(intselect==1)//int0
        {
            exchange=~exchange;
            ///채터링 제거 코드
            delay_ms(10);
            while(~PIND&0x01) ;
            delay_ms(10);
            EIFR = (1<<INTF0);
            intselect=0;
        }
        else if(intselect==2)//int4
        {
            ///시계 바꿀 자리 선택
            tslect++;
            if(tslect==3) tslect=0;

            ///채터링 제거 코드
            delay_ms(10);
            while(~PINE&0x10) ;
            delay_ms(10);
            EIFR = (1<<INTF4);
            intselect=0;
        }

    }

}
