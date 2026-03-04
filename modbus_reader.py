from pymodbus.client import ModbusSerialClient

PORT = "COM3"
BAUD = 9600

client = ModbusSerialClient(
    port=PORT,
    baudrate=BAUD,
    parity="N",
    stopbits=1,
    bytesize=8,
    timeout=1
)

client.connect()

def read_meter(slave_id):

    voltage = client.read_input_registers(0x0000, 2, slave=slave_id)
    current = client.read_input_registers(0x0006, 2, slave=slave_id)
    power = client.read_input_registers(0x0034, 2, slave=slave_id)
    energy = client.read_input_registers(0x0156, 2, slave=slave_id)

    return {
        "V": voltage.registers if voltage else None,
        "I": current.registers if current else None,
        "P": power.registers if power else None,
        "kWh": energy.registers if energy else None
    }


for i in range(1, 11):
    print(read_meter(i))
