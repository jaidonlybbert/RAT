/*
 * UART transmission
 * Cody Birkland
 * For TM4C123G
 * 
 * This code initializes a basic Universal Asynchronous Recieve and Transmit driver
 * that is connected to the top USB on the board. This allows you to write messages to a 
 * terminal window on your computer.
 */

//*****************************************************************************
//
// Include standard boolean (true, false, bool type) and standard integer 
// (uint32_t == unsigned integer 32-bit type, etc) libraries
//
//*****************************************************************************

#include <stdbool.h>
#include <stdint.h>

//*****************************************************************************
//
// Forward declaration of functions below main (prototypes):
//
//*****************************************************************************

void blink(long);			//LED blink for debugging with on-board LEDs
void delay(unsigned long);	//delay function - keeps processor busy
void clock_setup();			//initialize system clock at 50MHz
void configure_uart();			//setup gpio for LEDs
void uartwrite(unsigned char);
void say_hello();
void wait_for_pll();		//wait for system clock phase-locked-loop to be ready
void configure_RAT_uart_channel();
void uartread();

//*****************************************************************************
//
// Global Variables and Definitions
//
//*****************************************************************************

// the following constants are used throughout multiple methods:
#define port_F_base_address 0x40025000
#define wait 100000	//delay for blink flashes

//*****************************************************************************
//
// Start of Code:
//
//*****************************************************************************

int main() {
	clock_setup();
	blink(0x02);	    //blink red LED to show that clock is setup
	configure_uart();
    configure_RAT_uart_channel();

	say_hello();
	
	while (true)
		uartread();   //loop forever
}



void clock_setup() {
	//initializes and configures the main clock.
	//The clock-control block diagram can be found on page 222 of the datasheet.
	unsigned long * rcc = (unsigned long *)(0x400FE000 + 0x60);		//run-mode clock control register p.254
	unsigned long * rcc2 = (unsigned long *)(0x400FE000 + 0x70);	//run-mode clock control 2 register p.260 of datasheet

	*rcc2 = *rcc2 | (1<<31);		//RCC2 overrides RCC, so SYSDIV2 governs clock division
	*rcc2 = *rcc2 | (1<<11);		//bypass the PLL for safety while changing oscillator source (BYPASS2)
	*rcc = *rcc &(~(1<<22));		//make bit 22 low so that the system clock is undivided
	*rcc = *rcc & (~(0x1F<<6));		//XTAL clear set value
	*rcc = *rcc | (0x15<<6);		//XTAL set to 16mhz - tells PLL that its input is 16MHz
	*rcc2 = *rcc2 &(~(0xF<<4));		//nulls OSCSRC2, shuts off 32.768khz oscillator and uses 16MHz external crystal
	*rcc2 = *rcc2 &(~(0x1<<13));	//PWRON PLL2, the phase-lock-loop that boosts the source oscillator to 200MHz
	*rcc2 = *rcc2 & (~(0x3f<<23));	//clears SYSDIV2 bits 23 through 28, making the clock divider 1
	*rcc2 = *rcc2|(0x3<<23);		//assign SYSDIV2 to divide by 4, so that system divider yields 50MHz
	*rcc = *rcc|(0x1<<22);			//enable the system clock divider defined by SYSDIV above
	wait_for_pll();					//wait for pll steady-state
	*rcc2 = *rcc2 &(~(0x1<<11));	//shut off PLL bypass2 now that its stabilized

}



void wait_for_pll(){
	//Provides a delay until the PLL asserts that it is in steady-state by providing an interrupt
	unsigned long * ris = (unsigned long *)(0x400FE000 + 0x50);		//raw interrupt status register p.244

	while((!(*ris))&(0x1<<6)){		//once bit 6 in ris goes high, PLL is settled; run until then
		continue;
	}
}



void configure_uart() {
	// Add the configuration steps necessary to enable U0TX at
	//   115200bps
	//   8 data bits
	//   No parity
	//   1 Stop bit
	// See datasheet Section 14.4, pg 902-903 for Init Procedure
	// See datasheet Section 14.3.2, pg 896 for the Baudrate (115200) calculation
	// Also in Valvano 8.3.2 UART Device Driver, pg 319 in 4th ed
	
	unsigned long * RCGCUART = (unsigned long *)(0x400FE000 + 0x618); 	//Run mode clock gating control for UART, page 344
	unsigned long * RCGCGPIO = (unsigned long *)(0x400FE000 + 0x608); 	//Run-mode clock gating control for GPIO, page 340
	unsigned long * GPIOAFSEL =(unsigned long *) (0x40004000 + 0x420); 	//Alternate function select for Port A, page 672
	unsigned long * GPIOPCTL = (unsigned long *)(0x40004000 + 0x52C);	//GPIO port A control, page 689
	unsigned long * UARTCTL  = (unsigned long *)(0x4000C000 + 0x030);	//UART0 control page 918
	unsigned long * UARTIBRD = (unsigned long *)(0x4000C000 + 0x024);	//Integer part of baud rate divisor page 914
	unsigned long * UARTFBRD  =(unsigned long *) (0x4000C000 + 0x028);	//Fractional part of baud rate divisor page 915
	unsigned long * UARTLCRH  =(unsigned long *) (0x4000C000 + 0x02C);	//UART line control for word length and fifo enable, page 916
	unsigned long * GPIODEN = (unsigned long *)(0x40004000 + 0x51C);	//Digital enable register for gpio port A

	*RCGCUART = *RCGCUART | (1<<0); 	//Enable UART 0, which is connected to USB Tx/Rx 
	*RCGCGPIO = *RCGCGPIO | (1<<0); 	//Enable Port A. Port a is used for UART0 as per page 1351
	*GPIOAFSEL = *GPIOAFSEL | (0x3<<0);	//configure port A pins 0 and 1 as using periphrial
	*GPIOPCTL = *GPIOPCTL | (0x11);		//Make port A pins 0 and 1 UART0, see page 650 for pin assignments
	*UARTCTL = *UARTCTL | (1<<0); 		//Enable UART 0
	*GPIODEN = 0xFF;					//Enable all pins of port A
	blink(0x04);						//blink blue LED to indicate progress through register assignment

	//to obtain 115200 baud,  clock rate divisor is 27.126736 since system clock is 50MHz and HSE in  UARTCTL is clear.
	//thus the fractional part times 64 plus 0.5 is 8.61111. Assign 27 to UARTIBRD and floor(8.61111) to UARTFBRD. See p 869
	*UARTIBRD = 27;		//Integer part, hex equivalent of decimal 27
	*UARTFBRD = 8;		//fractional part, decimal 8
	*UARTLCRH = *UARTLCRH | ((0x3<<5)+(1<<4));	//Word length enable to 8 by asserting bits 5 and 6, enable fifo by asserting bit 4
		//leaving bit 1 and 3 as zero results in 1 stop bit and no parity bit. This UARTLCRH write must occur following any BRD change
	blink(0x04);					//blink blue LED again to indicate register assignment is complete
}

void configure_RAT_uart_channel() {
	unsigned long * RCGCUART = (unsigned long *)(0x400FE000 + 0x618); 	//Run mode clock gating control for UART, page 344
	unsigned long * RCGCGPIO = (unsigned long *)(0x400FE000 + 0x608); 	//Run-mode clock gating control for GPIO, page 340
	unsigned long * GPIOAFSEL =(unsigned long *) (0x40007000 + 0x420); 	//Alternate function select for Port D, page 672
	unsigned long * GPIOPCTL = (unsigned long *)(0x40007000 + 0x52C);	//GPIO port D control, page 689
	unsigned long * UARTCTL  = (unsigned long *)(0x4000E000 + 0x030);	//UART2 control page 918
	unsigned long * UARTIBRD = (unsigned long *)(0x4000E000 + 0x024);	//Integer part of baud rate divisor page 914
	unsigned long * UARTFBRD  =(unsigned long *) (0x4000E000 + 0x028);	//Fractional part of baud rate divisor page 915
	unsigned long * UARTLCRH  =(unsigned long *) (0x4000E000 + 0x02C);	//UART line control for word length and fifo enable, page 916
	unsigned long * GPIODEN = (unsigned long *)(0x40007000 + 0x51C);	//Digital enable register for gpio port D
    unsigned long * GPIOLOCK = (unsigned long *)(0x40007000 + 0x520);   //GPIO Lock register to unlock pd7; write 0x4C4F.434B 
    unsigned long * GPIOCR   = (unsigned long *)(0x40007000 + 0x524);   //GPIO CR register to allow writing to pd7
    
    *RCGCUART |= 0x04;      // Enable UART 2
    *RCGCGPIO |= 0x08;      // Enable Port D
    *GPIOLOCK = 0x4C4F434B; // Unlocks commit register to enable writing
    *GPIOCR  |= 0xC0;       // Enable edits to pd7 registers
    
    *GPIOAFSEL |= 0xC0;     // Enable AF for port D pins 6-7
    *GPIOPCTL |= 0x11000000;// Make PD6 and PD7 UART2 pins
    *UARTCTL |= 0x40;       // Enable clock to UART 2
    *GPIODEN = 0xC0;	    // Enable pins of port D
    
    // Set baud rate to 115200
    *UARTIBRD = 27;		//Integer part, hex equivalent of decimal 27
	*UARTFBRD = 8;		//fractional part, decimal 8
	*UARTLCRH = *UARTLCRH | ((0x3<<5)+(1<<4));
}



void uartwrite(unsigned char data) {
	// Use UARTFR, datasheet pg 911, TXFF bit to make sure the TX FIFO memory is not full
	// then UARTDR, datasheet pg 906 to write this new character into the TX FIFO
	unsigned long * UARTFR = (unsigned long *)(0x4000C000 + 0x018);		//UART Flag for fifo status, bit 5 = 1, fifo full
	unsigned long * UARTDR = (unsigned long *)(0x4000C000 + 0x00);		//UART transmits bits 0:7
	blink(0x02);		//blink red LED
	while(*UARTFR&(1<<5)){
		//wait until fifo is not full
	}
	*UARTDR = data;		//assign data register to current value of data, which is the current char
	blink(0x08);		//blink green LED
}

void uartread() {
    unsigned long * UARTFR = (unsigned long *)(0x4000C000 + 0x018);		//UART Flag for fifo status, bit 5 = 1, fifo full
	unsigned long * UARTDR = (unsigned long *)(0x4000C000 + 0x00);		//UART transmits bits 0:7

    // empty fifo
    while (!(*UARTFR&(0x10))) { 
        blink(0x08);
        unsigned char recv_data = *UARTDR;
        uartwrite(recv_data);
    }
}




void say_hello() {
	// Modify hello string constant to include your name
	char hello[] = "Hello EWU IEEE, from Cody Birkland\n\r";
	blink(0x08);	//blink green LED
	int count = 0;
	while (count<1) {
		// Send hello string one character at a time, repeating forever
		for(int i = 0; i<(sizeof(hello)/sizeof(hello[0]));i++){
			uartwrite(hello[i]);
			delay(10000);
		}
		count++;
	}
}



void delay(unsigned long d) {
	//This is a busy loop, will wait for a loop of length d
	for(int i=0; i<d; i++){
	}
}



void blink(long LED) {
	//passed in value is the bit number of the led pin in the gpio register. red: 0x02, blue: 0x04, green:0x08
	unsigned long *gpiodir = (unsigned long *) (port_F_base_address + 0x400 );
		//The direction registry address for IO config. Page 663 in the datasheet
	unsigned long *gpioafsel = (unsigned long *)(port_F_base_address + 0x420);
		//Alternate Function Select registry address for selecting GPIO or other pin functions. Page 671 in the datasheet
    unsigned long *gpioden = (unsigned long *) (port_F_base_address + 0x51c );
		//Digital enable registry address for enabling or disabling digital enable. Page 682 in the datasheet
    unsigned long * rcgcgpio = (unsigned long *)(0x400FE000+0x608); 
        //Run-Mode Clock Gating Control registry, page 340 of datasheet

	*rcgcgpio = (1<<5);	//enable and provide a clock to port F. This allows port F to operate by enabling its bus and register access
    
	*gpioafsel =  0x00;	//Choose GPIO using the alternative function select registry
	*gpiodir = 0x0E;	//Make LED pins outputs using the direction registry
	*gpiodir = (*gpiodir & ~(0x11));
	*gpioden = 0xFF;	//Enable all pins using the digital enable registry
	
	unsigned long * gpiodata = (unsigned long *) (0x40025000+(0x1F<<2));
		//data register address for definition of led states with mask for bits 4-0.

		*gpiodata = LED;	//selects color of LED. red: 0x02, blue: 0x04, green:0x08
		delay(wait);
		*gpiodata = 0x00;	//shut off LEDs
		delay(wait);
}
