Generic readme for skilled people.
This doc should help you to troubleshoot your unit.

1: Download http://www.pcausa.com/Utilities/UsbSnoop/ (for me it works under win7 too)

2: Start it

3: Install filter for 0x6666:0x5555 device

4: Start HeavyWeather, sync station

5: Stop filter

6: Copy Usbsnoop.log to linux

7: ./usbsnoop2libusb_nointerrupt.pl < Usbsnoop.log > test_28xx.c

8: gcc -lusb -o test_ws28xx.c

9: follow debug_usb_linux.txt

10: ./test_ws28xx (start logging debug output - (9))

11: ./HeavyWheatherService.py (start logging debug output - (9))

12: diff between the output of debug output

