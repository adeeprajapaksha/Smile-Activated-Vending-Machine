import serial
import time

def activate_motor(argument):
    # Replace 'COM9' with the appropriate COM port for your Arduino
    ser = serial.Serial('COM4', 9600, timeout=1)

    # Function to send a command to control the motors
    def send_command(command):
        ser.write(command.encode())

    try:
        # Add delay after opening the serial port
        time.sleep(2)

        # Turn on both motors
        print("Sending command 'H'")
        send_command('H')

        # Wait for 3 seconds
        time.sleep(2)

        # Turn off both motors
        print("Sending command 'L'")
        send_command('L')        

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Close the serial connection
        ser.close()

if __name__ == "__main__":
    activate_motor()
