#!/usr/bin/env python3
import cv2
import depthai as dai
import time

# Start defining a pipeline
pipeline = dai.Pipeline()

# Define a source - color camera
cam = pipeline.create(dai.node.ColorCamera)

# Script node
script = pipeline.create(dai.node.Script)
script.setScript("""
    import time
    ctrl = CameraControl()
    ctrl.setCaptureStill(True)
    while True:
        time.sleep(1)
        node.io['out'].send(ctrl)
""")

# XLinkOut
xout = pipeline.create(dai.node.XLinkOut)
xout.setStreamName("still")

# Connections
script.outputs['out'].link(cam.inputControl)
cam.still.link(xout.input)

# Connect to device with pipeline
with dai.Device(pipeline) as device:
    i = 0
    while True:
        time.sleep(1)
        img = device.getOutputQueue("still").get()
        cv_frame = img.getCvFrame()
        cv2.imshow('still', cv_frame)
        cv2.imwrite("{}.jpeg".format(i), cv_frame)
        i += 1
        if cv2.waitKey(1) == ord('q'):
            break
