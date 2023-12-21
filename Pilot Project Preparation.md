# Pilot Project Preparation
* Here's a guide to prepare the camera system for pilot project.
(These steps assume that you are using the original RPi 4 host device)
* The password for RPi and server can be found on Asana

1. On the RPi 4, add the necessary wifi connection. The RPi will use this connection during pilot project.
```
sudo nano /etc/netplan/50-cloud-init.yaml
```
$~~~~~~~~~$ Enter the wifi's name and password in the format below
```
```
$~~~~~~~~~$ Apply the netplan and reboot the RPi
```
sudo netplan generate
sudo netplan apply
sudo reboot
```

2. Connect the camera system's hardware. Refer to 
3. Mount cameras on TP. Refer to
4. Connect system to TP's power and CAN Bus. Check the resistance between CAN High and CAN Low
5. Turn on RM to verify that camera system can be powered. The script to capture images should automatically run at this moment.
6. From the laptop, verify that camera system is connected to wifi. The laptop must be using the same wifi network.
```
sshcam
```
7. Control the RM manually to move it up and down. From the laptop, open a new terminal. Check the server to verify that images are being sent and images aren't too dark or bright
```
sshdash
cd /images/LB1/{date}/{time}
```
8. From the laptop, open another terminal. Check error log to see if there is error during the run
```
sshcam
cat /Project/Camera/log/debug.log
```


