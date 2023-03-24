from typing import Optional

from construct import Int8ul, Int16ul, Int32ul, Struct, Array, Byte

from victron_ble.devices.base import Device, DeviceData, OperationMode


class LithiumBatteryData(DeviceData):
    def get_battery_voltage(self) -> float:
        """
        Return the battery voltage in volts
        """
        voltage = self._data["battery_voltage"]
        if voltage == 0x0FFF:
            return None
        return voltage

    def get_temperature(self) -> float:
        """
        Return the battery temperature in °C
        """
        temperature = self._data["temperature"] & 0x7F
        if temperature == 0x7F:
            return None
        return temperature


class LithiumBattery(Device):
    PACKET = Struct(
        "bms_flags" / Int32ul,
        "battery_error" / Int16ul,
        "cell_voltages" / Array(7, Byte),
        "battery_voltage_balancer_status" / Int16ul,
        "temperature" / Int8ul,
    )

    def parse(self, data: bytes) -> LithiumBatteryData:
        decrypted = self.decrypt(data)
        pkt = self.PACKET.parse(decrypted)

        print(pkt.battery_voltage_balancer_status)
        parsed = {
            "bms_flags": pkt.bms_flags,
            "battery_voltage": (pkt.battery_voltage_balancer_status & 0x0FFF) / 100,
            "temperature": pkt.temperature - 40
        }

        return LithiumBatteryData(self.get_model_id(data), parsed)
