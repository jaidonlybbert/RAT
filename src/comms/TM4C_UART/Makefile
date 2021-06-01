all: rat_uart.bin

%.o: %.c
	@echo arm-none-eabi-gcc -ggdb \
		-mthumb -mcpu=cortex-m4 -mfpu=fpv4-sp-d16 \
		-mfloat-abi=softfp -ffunction-sections \
		-fdata-sections -MD -std=c99 -Wall \
		-pedantic -c -o ${@} ${<}
	@arm-none-eabi-gcc -ggdb \
		-mthumb -mcpu=cortex-m4 -mfpu=fpv4-sp-d16 \
		-mfloat-abi=softfp -ffunction-sections \
		-fdata-sections -MD -std=c99 -Wall \
		-pedantic -c -o ${@} ${<}

rat_uart.axf: tiva.ld
rat_uart.axf: startup.o
rat_uart.axf: UART.o

%.axf:
	@echo arm-none-eabi-ld \
	       -T tiva.ld --entry ResetISR --gc-sections \
	       -o ${@} $(filter %.o %.a, ${^})
	@arm-none-eabi-ld \
	       -T tiva.ld --entry ResetISR \
	       -o ${@} $(filter %.o %.a, ${^})


%.bin: %.axf
	@echo arm-none-eabi-objcopy -O binary ${@:.bin=.axf} ${@}
	@arm-none-eabi-objcopy -O binary ${@:.bin=.axf} ${@}


clean:
	@rm -rf *.bin *.axf *.o *.d
