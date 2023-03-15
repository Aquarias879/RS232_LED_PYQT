import os
import sys
import time 
import datetime
import serial
import serial.tools.list_ports
from PyQt5.QtCore import QTimer,Qt
from PyQt5.QtWidgets import QApplication, QComboBox, QLineEdit, QPushButton, QWidget, QTextEdit,QLabel,QVBoxLayout,QHBoxLayout
from PyQt5.QtGui import QIcon
#import struct

class SerialSender(QWidget):
    def __init__(self):
        super().__init__()
        # Create a QTimer to update the list of available COM ports
        self.timer = QTimer(self)
        #self.timer.timeout.connect(self.update_com_ports)
        #refresh = self.combo_box.clear()
        #self.timer.start(1000) # Set the timer to trigger every 1 second
        
        #icon = QIcon("./Refresh_icon")
        # Create a QComboBox widget to display a list of available COM ports
        self.port_label = QLabel("Select Com Port:", self)
        self.combo_box = QComboBox(self)
        self.re_bt = QPushButton("Refresh",self)
        #self.re_bt.setIcon(QIcon('./Refresdh.ico'))
        self.re_bt.setFixedSize(50, 20)
        self.re_bt.clicked.connect(self.update_com_ports)
        #self.re_bt.setGeometry(10,10,50,20)

        # create lebel for translate text to hex
        self.translates_label = QLabel("Input Text:", self)

        # create lineEdite for translate text to hex
        self.translates_edit = QLineEdit(self)

        #tranlate bt 
        self.translates_bt = QPushButton("Send",self)
        self.translates_bt.clicked.connect(self.send_translate_data)
        self.translates_bt.setFixedSize(60,20)

        #size_calculate
        self.size_label = QLabel("input other command:",self)
        self.size_edit = QLineEdit(self)
        self.size_bt = QPushButton("Send",self)
        self.size_bt.clicked.connect(self.cal_size)
        self.size_bt.setFixedSize(60,20)

        self.hex_res_label = QLabel("Enocoded:", self)
        self.response_tran = QLabel(self)
        #self.response_tran.setFixedSize(400, 20)

        # Create a QLabel widget for the hex data field
        self.hex_data_label = QLabel("Input Command:", self)

        # Create a QLineEdit widget to allow the user to enter the hex data to send
        self.hex_data_edit = QLineEdit(self)

        # Create a QPushButton widget to send the data to the serial device
        self.send_button = QPushButton("Send", self)
        self.send_button.clicked.connect(self.send_data)
        self.send_button.setFixedSize(60,20)
        # Create a QTextEdit widget to display the response from the serial device
        self.response_edit = QTextEdit(self)

        #layout_v = QVBoxLayout()
        #layout_v.addWidget(self.re_bt,Qt.AlignRight)

        layout1 = QHBoxLayout()
        # Add the widgets to the layout
        layout1.addWidget(self.combo_box)
        layout1.addWidget(self.re_bt)

        layout2 = QHBoxLayout()
        
        layout2.addWidget(self.translates_edit)
        layout2.addWidget(self.translates_bt)

        layout3 = QHBoxLayout()
        layout3.addWidget(self.size_edit)
        layout3.addWidget(self.size_bt)

        layout4 = QHBoxLayout()
        layout4.addWidget(self.hex_data_edit)
        layout4.addWidget(self.send_button)

        layout5 = QVBoxLayout()
        layout5.addWidget(self.port_label)
        layout5.addLayout(layout1)
        layout5.addWidget(self.translates_label)
        layout5.addLayout(layout2)
        layout5.addWidget(self.size_label)
        layout5.addLayout(layout3)
        layout5.addWidget(self.hex_data_label)
        layout5.addLayout(layout4)
        #layout2.addLayout(layout1,layout2,layout3)
        layout5.addWidget(self.hex_res_label)
        layout5.addWidget(self.response_tran)
        layout5.addWidget(self.response_edit)
        
        # Set the layout of the main widget
        self.setLayout(layout5)
        #self.setLayout(layout_v)

        self.setGeometry(300, 300, 350, 450)
        self.setWindowTitle("Serial Sender")
        self.show()
    
    def update_com_ports(self):
        # Get a list of available COM ports
        self.com_ports = serial.tools.list_ports.comports()

        # If there are no available COM ports, display an error message
        if len(self.com_ports) == 0:
            print("No COM ports found")
            #sys.exit()

        # Update the combo_box widget with the new list of available COM ports
        self.combo_box.clear()
        for port, desc, hwid in self.com_ports:
            self.combo_box.addItem(port)
            self.combo_box.setCurrentIndex(0)

    def send_translate_data(self):
        # Get the input string from the translate_edit widget
        input_string = self.translates_edit.text()
        outputString = input_string.encode('utf-16').hex()

        hex_values = [outputString[i:i+2] for i in range(0, len(outputString), 2)]
        merged_hex = b''.join([bytes.fromhex(h) for h in hex_values])
        #merged_hex = b''.join(hex_values)
        header = b'\xA1'
        end = b'\x51'
        sub_cmd = b'\x02'
        length = len(hex_values) + 6
        minus_len = 255 - length
        length_field = length.to_bytes(1, 'big')
        #length_field = struct.pack('>L', length)
        minus_len_field = minus_len.to_bytes(1, 'big')
        #minus_len_field = struct.pack('>L', minus_len)
        first_msg = header + length_field+ minus_len_field +sub_cmd + merged_hex 
        check_sum = hex(sum(first_msg)) 
        up_check_sum = bytes.fromhex(check_sum[-2:])

        msg = first_msg + up_check_sum + end

        hex_string = ' '.join(hex(b)[2:].rjust(2, '0') for b in msg)
        self.response_tran.setText(hex_string)
        self.hex_data_edit.setText(hex_string)
        #self.send_data(hex_string)
    def cal_size(self):
        input_size = self.size_edit.text()
        self.hex_data_edit.setText(input_size)

    def send_data(self):
        # Open a serial connection to the selected port
        selected_port = self.combo_box.currentText()
        ser = serial.Serial(
            port=selected_port,
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=2,
            write_timeout=5
        )

        ser.isOpen()
        # Get the current time
        now = datetime.datetime.now()
        # Format the timestamp as a string
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

        # Get the hex data to send from the QLineEdit widget
        hex_data = self.hex_data_edit.text()
        try:
            # Convert the hex string to a bytes object
            data = bytes.fromhex(hex_data)
        except ValueError:
            # Display an error message if the hex string is invalid
            self.response_edit.append("Error: Invalid hex string")
            return
        # Convert the hex string to a bytes object
        #data = bytes.fromhex(hex_data)
        
        comand = timestamp+ ": Command >>>> " + hex_data
        # Send the data to the serial device
        #ser.write(data * 10)
        try:
            # code that may throw the SerialTimeoutException error
            ser.write(data)
        except serial.serialutil.SerialTimeoutException:
            # code to handle the SerialTimeoutException error
            print("Timeout error occurred")

        # Read the response from the serial device
        response = ser.read()
        # Convert the response to a hex string
        response_hex = response.hex()
        response = timestamp + ": Response <<< " + response_hex
        ser.close()

        # Print the timestamp and response to the console
        print(f"{timestamp}: {response}")
        # Display the response in the QTextEdit widget
        self.response_edit.append(comand)
        self.response_edit.append(response)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    sender = SerialSender()
    sys.exit(app.exec_())