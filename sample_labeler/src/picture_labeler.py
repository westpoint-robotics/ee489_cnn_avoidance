#!/usr/bin/env python
import rospy
from sensor_msgs.msg import Joy, Image
from std_msgs.msg import Bool
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge, CvBridgeError
import cv2


global buttons, axes, state, num, trial_num, data_set, current,bridge
bridge = CvBridge()
buttons = [0,0,0,0,0,0,0,0,0,0,0]
axes = [0,0,0,0,0,0,0,0]
num=0
data_set="test4"
trial_num=0
current='x'

state = False;
move_cmd = Twist()


def joy_callback(data):
    global axes,buttons
    buttons = data.buttons
    axes = data.axes
    #print buttons  
    #print axes

def image_callback(data):
    global num, trial_num, data_set, current,bridge
    try:
        cv_image = bridge.imgmsg_to_cv2(data, "bgr8")
        #print current
        if current != 'x':
            num+=1
            pub_string = "/home/user1/data/"+str(data_set)+"/"+str(current)+"/trial_"+str(trial_num)+"_img_"+str(num)+"_"+str(current)+".png"
            #pub_string="/home/user1/test.png"
            cv2.imwrite( pub_string , cv_image )
            print "wrote image"
    except CvBridgeError as e:
      print(e)

if __name__ == '__main__':
    rospy.init_node('drive_node', anonymous=True)
    rospy.Subscriber("joy", Joy, joy_callback)
    rospy.Subscriber("usb_cam_node/image_raw",Image,image_callback)
    cmd_vel = rospy.Publisher('cmd_vel', Twist, queue_size=10)
    rate = rospy.Rate(60);
    #trial_num = rospy.get_param('/trial_num')
    #data_set = rospy.get_param('/data_set')
    #bridge = CvBridge()
    global current
    while not rospy.is_shutdown():
        if (buttons[3] == 1):
            if(state==1):
                current='x'
            state = not state
            rospy.sleep(0.2)
        if state == 0:
            #print "teleop"
            move_cmd.angular.z = -axes[0] 
            move_cmd.linear.x = axes[1] 
            #print move_cmd
        else:
            #record images
            #print "recording"
            if buttons[2] == 1:
                #data.append('l')
                current = 'l'
                #rospy.loginfo("left")
                move_cmd.linear.x = 0.35
                # turn at 1 radians/s
                move_cmd.angular.z = -1.0
            elif buttons[1] == 1:
                #data.append('r')
                current = 'r'
                #rospy.loginfo("right")
                move_cmd.linear.x = 0.35
                # turn at -1 radians/s
                move_cmd.angular.z = 1.0
            elif buttons[0] == 1:
                current = 'x'
                #rospy.loginfo("Stop")
                move_cmd.linear.x = 0
                # turn at 0 radians/s
                move_cmd.angular.z = 0
            else:
                #data.append('s')
                current = 's'
                #rospy.loginfo("Straight")
                move_cmd.linear.x = .35
                # let's turn at 0 radians/s
                move_cmd.angular.z = 0
            #print move_cmd
        # publish the velocity
        cmd_vel.publish(move_cmd)
        #self.drive_pub.publish(current)
            
        
        rate.sleep()        
        #print buttons
