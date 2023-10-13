import pickle
from keras.models import load_model
import sim
from time import sleep as delay
import numpy as np
import cv2
import sys

print('Program started')
sim.simxFinish(-1)
clientID = sim.simxStart('127.0.0.1', 19999, True, True, 5000, 5)

lSpeed = 0
rSpeed = 0

if (clientID != -1):
    print('Connected to remote API server')

else:
    sys.exit('Failed connecting to remote API server')


errorCode, left_motor_handle = sim.simxGetObjectHandle(
    clientID, 'Pioneer_p3dx_leftMotor', sim.simx_opmode_oneshot_wait)
errorCode, right_motor_handle = sim.simxGetObjectHandle(
    clientID, 'Pioneer_p3dx_rightMotor', sim.simx_opmode_oneshot_wait)

errorCode, camera_handle = sim.simxGetObjectHandle(
    clientID, 'cam1', sim.simx_opmode_oneshot_wait)
delay(1)

returnCode, resolution, image = sim.simxGetVisionSensorImage(
    clientID, camera_handle, 0, sim.simx_opmode_streaming)
delay(1)


model = load_model('res/Models/Ai_Car-0.9653284549713135.h5')


dict_file = open("res/Data/ai_car.pkl", "rb")
category_dict = pickle.load(dict_file)


try:
    while (1):
        returnCode, resolution, image = sim.simxGetVisionSensorImage(
            clientID, camera_handle, 0, sim.simx_opmode_buffer)
        im = np.array(image, dtype=np.uint8)
        im.resize([resolution[0], resolution[1], 3])

        im = cv2.flip(im, 0)
        im = cv2.resize(im, (512, 512))
        im = cv2.cvtColor(im, cv2.COLOR_RGB2BGR)

        errorCode = sim.simxSetJointTargetVelocity(
            clientID, left_motor_handle, lSpeed, sim.simx_opmode_streaming)
        errorCode = sim.simxSetJointTargetVelocity(
            clientID, right_motor_handle, rSpeed, sim.simx_opmode_streaming)

        test_img = cv2.resize(im, (50, 50))
        test_img = cv2.cvtColor(test_img, cv2.COLOR_BGR2GRAY)
        test_img = test_img/255
        test_img = test_img.reshape(1, 50, 50, 1)

        results = model.predict(test_img)
        label = np.argmax(results, axis=1)[0]
        acc = int(np.max(results, axis=1)[0]*100)

        print(f"Moving : {category_dict[label]} with {acc}% accuracy.")

        if (label == 0):
            lSpeed = 0.2
            rSpeed = 0.2
        elif (label == 1):
            lSpeed = -0.1
            rSpeed = 0.2
        elif (label == 2):
            lSpeed = 0.2
            rSpeed = -0.1
        else:
            lSpeed = 0
            rSpeed = 0
        label = -1

        cv2.imshow("data", im)
        com = cv2.waitKey(1)
        if (com == ord('q')):
            lSpeed = 0
            rSpeed = 0
            break

    cv2.destroyAllWindows()
    errorCode = sim.simxSetJointTargetVelocity(
        clientID, left_motor_handle, lSpeed, sim.simx_opmode_streaming)
    errorCode = sim.simxSetJointTargetVelocity(
        clientID, right_motor_handle, rSpeed, sim.simx_opmode_streaming)
except:
    cv2.destroyAllWindows()
