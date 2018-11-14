#!/usr/bin/env python
import rospy
import numpy as np
from sensor_msgs.msg import Joy, Image, LaserScan
from std_msgs.msg import Bool
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge, CvBridgeError
import cv2


global buttons, axes, state, num, trial_num, data_set, current, bridge, ranges, ang_start, ang_increment
bridge = CvBridge()
buttons = [0,0,0,0,0,0,0,0,0,0,0]
axes = [0,0,0,0,0,0,0,0]
num=0
data_set="14Nov18"
trial_num=1
current='x'
ranges = [1,1,1]
ang_start=-2.35619449615 
ang_increment=0.00613592332229

state = False;
move_cmd = Twist()

def joy_callback(data):
    global axes,buttons
    buttons = data.buttons
    axes = data.axes
    #print buttons  
    #print axes

def laser_callback(data):
    global ranges
    ranges = data.ranges

def image_callback(data):
    global num, trial_num, data_set,bridge, current, ranges, ang_start, ang_increment
    try:
        cv_image = bridge.imgmsg_to_cv2(data, "bgr8")
        #catch box for point cloud
        cv2.rectangle(cv_image,(240,160),(400,320),(255,255,255),1) 
        counter=0
        #convert polar to rectangular then plot        
        for x in ranges:
            if x<.4 and x>.2:
                angle= ang_start + (counter*ang_increment)+1.43889
                xcord= int(round(250*x*np.cos(angle) + 320))
                ycord= int(round(-250*x*np.sin(angle) + 240))
                cv2.circle(cv_image,(xcord,ycord),4,(0,0,255),-1)
            counter= counter +1
        if current != 'x': #IF IT IS MOVING
            num+=1
            pub_string = "/home/rrc/data/"+str(data_set)+"/"+str(current)+"/trial_"+str(trial_num)+"_img_"+str(num)+"_"+str(current)+".png"
            cv2.imwrite( pub_string , cv_image )
            print "wrote image"
    except CvBridgeError as e:
      print(e)
    try:
        # publish the image with line overlayed to image_view node in launch file
        image_pub.publish(bridge.cv2_to_imgmsg(cv_image, "bgr8"))
    except CvBridgeError as e:
        print(e)


if __name__ == '__main__':
    rospy.init_node('drive_node', anonymous=True) #init. our node
    rospy.Subscriber("joy", Joy, joy_callback) #subscribe to the controller
    rospy.Subscriber("cv_camera_node/image_raw",Image,image_callback) #subscribe to camera
    rospy.Subscriber("scan", LaserScan, laser_callback)
    #create an image publisher to publish the altered camera feed
    image_pub = rospy.Publisher("image_topic",Image)
    cmd_vel = rospy.Publisher('/mobile_base/commands/velocity', Twist, queue_size=10) #publish vel.
    rate = rospy.Rate(60);
    #trial_num = rospy.get_param('/trial_num')
    #data_set = rospy.get_param('/data_set')
    bridge = CvBridge()
    while not rospy.is_shutdown():
        if (buttons[3] == 1): #IF Y PRESSED
            if(state==1): 
                current='x'
            state = not state #STATE GOES ON
            rospy.sleep(0.2)
        if state == 0:
            print "teleop"
            move_cmd.angular.z = -axes[0] 
            move_cmd.linear.x = axes[1] 
            #print move_cmd
        else: #IF OUR STATE IS ON (WHICH IS Y PRESS ACTIVATES):
            #record images
            print "recording"
            if buttons[1] == 1: #PRESS B
                #data.append('l')
                current = 'r'
                #rospy.loginfo("left")
                move_cmd.linear.x = .1
                # turn at 1 radians/s
                move_cmd.angular.z = -.80
            elif buttons[2] == 1: #PRESS X
                #data.append('r')
                current = 'l'
                #rospy.loginfo("right")
                move_cmd.linear.x = .1
                # turn at -1 radians/s
                move_cmd.angular.z = .80
            elif buttons[0] == 1: #PRESS A
                current = 'x'
                #rospy.loginfo("Stop")
                move_cmd.linear.x = 0
                # turn at 0 radians/s
                move_cmd.angular.z = 0
            else:
                #data.append('s')
                current = 's'
                #rospy.loginfo("mStraight")
                move_cmd.linear.x = .12
                # let's turn at 0 radians/s
                move_cmd.angular.z = 0
            #print move_cmd
        # publish the velocity
        cmd_vel.publish(move_cmd)
        #self.drive_pub.publish(current)
            
        
        rate.sleep()        
        #print buttons
