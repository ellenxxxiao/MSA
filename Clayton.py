"""
Shulunsaina (Ellen) Xiao, Monash University.
For MSA Bootcamp #2 Cloud Computing. Skeleton used is sourced from Microsoft.
"""
import random
import time
import threading
from azure.iot.device import IoTHubDeviceClient, Message, MethodResponse

# The device connection string to authenticate the device with your IoT hub.
# Using the Azure CLI:
# az iot hub device-identity show-connection-string --hub-name {YourIoTHubName} --device-id MyNodeDevice --output table
CONNECTION_STRING = "HostName=MSA-cloud2.azure-devices.net;DeviceId=Clayton;SharedAccessKey=/OzxRtVPHchEyhA70NeOI4mcTrVB+leO1AezN5XkE0k="

# Define the JSON message to send to IoT Hub.
MSG_TXT = '{{"customerEnter": {customerEnter}, "customerExit": {customerExit}, "sales": {sales}, "temperature": {temperature}, "nearestDegree": {temp_deg}, "time": {time}, "location": {location}}}'

INTERVAL = 1
TEMPERATURE = random.randrange(25, 31)
LOCATION = "\"New York, USA\""
LOWER_BOUND = 15
UPPER_BOUND = 17
TEMP_BONUS = 20
TIME_BONUS = 10


def iothub_client_init():
    # Create an IoT Hub client
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
    return client


def device_method_listener(device_client):
    global INTERVAL
    while True:
        method_request = device_client.receive_method_request()
        print(
            "\nMethod callback called with:\nmethodName = {method_name}\npayload = {payload}".format(
                method_name=method_request.name,
                payload=method_request.payload
            )
        )
        if method_request.name == "SetTelemetryInterval":
            try:
                INTERVAL = int(method_request.payload)
            except ValueError:
                response_payload = {"Response": "Invalid parameter"}
                response_status = 400
            else:
                response_payload = {"Response": "Executed direct method {}".format(method_request.name)}
                response_status = 200
        else:
            response_payload = {"Response": "Direct method {} not defined".format(method_request.name)}
            response_status = 404

        method_response = MethodResponse(method_request.request_id, response_status, payload=response_payload)
        device_client.send_method_response(method_response)


def iothub_client_telemetry_sample_run():
    global TEMPERATURE
    try:
        client = iothub_client_init()
        print("IoT Hub device sending periodic messages, press Ctrl-C to exit")

        # Start a thread to listen
        device_method_thread = threading.Thread(target=device_method_listener, args=(client,))
        device_method_thread.daemon = True
        device_method_thread.start()

        start = 9
        customerInStore = 0
        while True:
            base_temperature = TEMPERATURE
            print(base_temperature)
            if 7 < start < 16:
                temperature = base_temperature + (random.random() * 4.1)
            else:
                temperature = base_temperature - (random.random() * 4)
            bonus = 0
            if temperature > 30:
                bonus += TEMP_BONUS
            if LOWER_BOUND <= start <= UPPER_BOUND:
                bonus += TIME_BONUS
            customerEnter = random.randint(0, 10) + bonus
            customerInStore += customerEnter
            customerExit = random.randint(0, customerInStore)
            customerInStore -= customerExit

            sales = 0
            prices = [8, 15, 16, 21]
            for _ in range(customerExit):  # customers pay when they exit
                sales += prices[random.randint(0, 3)]

            msg_txt_formatted = MSG_TXT.format(customerEnter=customerEnter, customerExit=customerExit,
                                               sales=sales, temperature=temperature, temp_deg=round(temperature), time=start, location=LOCATION)
            message = Message(msg_txt_formatted)
            start += 1
            if start == 24:
                start = 0
                TEMPERATURE = random.randrange(26, 29)

            # Add a custom application property to the message.
            # An IoT hub can filter on these properties without access to the message body.
            if customerInStore > 30:
                message.custom_properties["CrowdAlert"] = "true"
            else:
                message.custom_properties["CrowdAlert"] = "false"

            # Send the message.
            print("Sending message: {}".format(message))
            client.send_message(message)
            print("Message sent")
            time.sleep(INTERVAL)

    except KeyboardInterrupt:
        print("IoTHubClient sample stopped")


if __name__ == '__main__':
    print("IoT Hub Quickstart #2 - Simulated device")
    print("Press Ctrl-C to exit")
    iothub_client_telemetry_sample_run()

if __name__ == '__main__':
    print("IoT Hub Quickstart #2 - Simulated device")
    print("Press Ctrl-C to exit")
    iothub_client_telemetry_sample_run()
