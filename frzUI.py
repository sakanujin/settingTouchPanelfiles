from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.togglebutton import ToggleButton # for toggle
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.config import Config
from kivy.properties import BooleanProperty
from kivy.properties import NumericProperty
from kivy.clock import Clock
from functools import partial 
################################################# 
# if you use the code for Raspberry Pi, turn into True,  if use PC pls put False
RASPBERRY_CODE = True
#RASPBERRY_CODE = False

if (RASPBERRY_CODE == True):
    import pt100
    import RPi.GPIO as GPIO

import time
################################################# 
#Config.set('graphics', 'width', '600')
#Config.set('graphics', 'height', '100')
#Window.fullscreen = 'auto'
#Window.fullscreen = True
#Config.set('input', 'mouse', 'mouse, disable_on_activity')
Config.set('input', 'mouse', 'mouse, disable_multitouch')
Config.set('modules', 'inspector', '')

#Window.size = (800,530)
#Window.size = (800,330)
Window.size = (800,500)
################################################# 
#GPIO  Test 
#DEBUG=True
DEBUG=False

#import RPi.GPIO as GPIO       # later delete by saka
#GPIO.setmode(GPIO.BCM)        # later delete by saka
if (DEBUG == True):
    print("now Debug mode ")
    import RPi.GPIO as GPIO    # later delete by saka
    GPIO.setmode(GPIO.BCM)     # later delete by saka
    GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # ERR State # later delete by saka
    GPIO.setup(13, GPIO.OUT, initial=GPIO.LOW)   # later delete by saka

if (RASPBERRY_CODE == True):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(21, GPIO.OUT,initial=GPIO.HIGH) #CDU  
    GPIO.setup(16, GPIO.OUT,initial=GPIO.HIGH) #AGI
    GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)# ERR State 
    GPIO.setup(13, GPIO.OUT, initial=GPIO.LOW) #Buzzer out
################################################# 
#GLOBAL variables
glob_CDU_stat = 0
glob_AGI_stat = 2  #1 Renzoku,  2 Danzoku 
glob_current_temp = 0
glob_setting_temp = -30
glob_delay        = 1.5
#glob_delay        = 1
glob_event_type = ''
################################################# 
def Err_and_Bzr ():
    if (RASPBERRY_CODE == True):
    #if (RASPBERRY_CODE == False):
        if GPIO.input(12) == 1:
            print ("****************** CAUTION *************")
            print ("             Error Occur")
            print ("****************************************")
            GPIO.output(13, 1);
        else :
           # print ("////////////////////////////////////////")
           print ("//now stable, and do well everything//")
           # print ("////////////////////////////////////////")


################################################# 
def control_OnOff_by_temp():
    # print("What is: {}".format(glob_AGI_stat))
    # print("#DEBUG# On/Off delay time is ", glob_delay)
    # print("now:{}, set:{}".format(now, setting))
    global glob_current_temp
    global glob_setting_temp
    global glob_AGI_stat
    global glob_CDU_stat
    if (glob_current_temp >= (glob_setting_temp + 2)):
        print("************** CDU ON ************")
        glob_CDU_stat = 1
        if(RASPBERRY_CODE == True):
            GPIO.output(21, 1)
            if (glob_AGI_stat == 2):# AGI Danzoku 
                print("&&&&&&&& AGI DANZOKU == ON with CDU &&&&&&&&&&&")
                GPIO.output(16, 1)
    elif (glob_current_temp <= (glob_setting_temp - 2)):
        print("///////////// CDU OFF ////////////")
        glob_CDU_stat = 0
        if(RASPBERRY_CODE == True):
            GPIO.output(21, 0)
            if (glob_AGI_stat == 2):# AGI Danzoku 
                print("||||||||  AGI DANZOKU  OFF with CDU |||||||||||")
                GPIO.output(16, 0)
                print("AGI OFF" )
################################################# 
class Screen_One(Screen): # 3rd Screen
    stMin =   StringProperty()
    valMin =   3

    def __init__(self, **kwargs):
        self.valMin = 3
        self.stMin = str(3)
        super(Screen_One, self).__init__(**kwargs)
        
    def btcUP(self): #UP
        if('Mouse' in glob_event_type):
            self.valMin = self.valMin + 1
            self.stMin  = str(self.valMin)

    def btcDOWN(self):
        if('Mouse' in glob_event_type):
            self.valMin = self.valMin - 1
            self.stMin  = str(self.valMin)
            #self.set_num = self.set_num - 1

    def btcDelaySet(self):  
        global glob_delay
        if('Mouse' in glob_event_type):
            glob_delay = self.valMin 
        # print("#DEBUG# delay time is set " ,glob_delay)

    def btRenzoku(self):
        global glob_AGI_stat

        if('Mouse' in glob_event_type):
            glob_AGI_stat = 1
            #print("AGI: {}".format(glob_AGI_stat))
            if(RASPBERRY_CODE == True):
                GPIO.output(16, 1) # always AGI ON  
                print ("AGI  RENZOKU   ALWAYS ON")

    def btDanzoku(self):
        global glob_AGI_stat
        if('Mouse' in glob_event_type):
            glob_AGI_stat = 2
            #print("AGI: {}".format(glob_AGI_stat))

class Screen_KitchenTimer(Screen):
    is_countdown = BooleanProperty(False)
    left_time = NumericProperty(0)
    temp_now_KT = StringProperty()

    def __init__(self, **kwargs):
        global glob_current_temp
        super(Screen_KitchenTimer, self).__init__(**kwargs)
        if (RASPBERRY_CODE  == True):
            self.temp_now_KT = str(pt100.pt100GetTmp())
            glob_current_temp = int(self.temp_now_KT)
            Clock.schedule_interval(lambda dt: self.tempUpdate(), 1)

    def tempUpdate(self):
        global glob_current_temp
        if (RASPBERRY_CODE  == True):
            self.temp_now_KT = str(pt100.pt100GetTmp())
            glob_current_temp = int(self.temp_now_KT)
    
    def on_command(self, command):
        if('Mouse' in glob_event_type):
            if command == '+10 sec':
                self.left_time += 10
                if (self.left_time > 990):
                    self.left_time = 990
            elif command == '+5 sec':
                self.left_time += 5
                if (self.left_time > 990):
                    self.left_time = 990
            elif command == '-5 sec':
                self.left_time -= 5
                if (self.left_time < 0):
                    self.left_time = 0
            elif command == '-10 sec':
                self.left_time -= 10
                if (self.left_time < 0):
                    self.left_time = 0
            elif command == 'start/stop':
                if self.is_countdown:
                    self.stop_timer()
                elif self.left_time > 0:
                    self.start_timer()
            elif command == 'reset':
                    self.stop_timer()
                    self.left_time   = 0

    def on_countdown(self, dt):
        self.left_time -=1
        if self.left_time == 0:
            self.is_countdown = False
            return False

    def start_timer(self):
        self.is_countdown = True
        #Clock.schedule_interval(self.on_countdown, 1.0) #sec 
        Clock.schedule_interval(self.on_countdown, 60.0)  #min
        pass

    def stop_timer(self):
        self.is_countdown = False
        Clock.unschedule(self.on_countdown)
        pass

################################################
class Screen_AGI(Screen):
    renzokku = 1
    danzok   = 0

    def __init__(self, **kwargs):
        super(Screen_AGI, self).__init__(**kwargs)

    pass
################################################
class Screen_Alert(Screen):
    smalt = ScreenManager() 

    def __init__(self, **kwargs):
        super(Screen_Alert, self).__init__(**kwargs)

    def btnBack(self):
        self.smalt.add_widget(Display(name='Display'))
        #self.smpy.add_widget(Screen_Alert(name='Screen_Alert'))
        #self.smpy.add_widget(Screen_One(name='Screen_One'))
        self.smalt.current = 'Display'
        SM02App().build()
        print("Move to main view")

    def btnBuzzOff(self):
        GPIO.output(13, 0);



################################################

#class TextWidget(Screen):
class Screen_Home(Screen):
    #text1 = StringProperty()
    #text2 = StringProperty()
    #text3 = StringProperty()
    text4 = StringProperty()
    temp_now = StringProperty()
    temp_set = StringProperty()
    set_num  = -30   

    def __init__(self, **kwargs):
        #super(TextWidget, self).__init__(**kwargs)
        super(Screen_Home, self).__init__(**kwargs)
        #self.text1 = 'オフ'
        #self.text2 = 'UP'
        #self.text3 = 'DOWN'
        self.text4 = 'オフ'
        #self.temp_now = str(25)

        if (RASPBERRY_CODE == True):
            self.temp_now = str(pt100.pt100GetTmp())
            #self.temp_now = str(25)
        else: 
            self.temp_now = str(25)

        #self.temp_set = str(self.temp_now)
        self.temp_set = str(self.set_num)
        self.set_num  = int(self.temp_set)

        Clock.schedule_interval(lambda dt: self.tempUpdate(), 1)

    def buttonClicked(self):  

        if self.text4 == "オン":

            self.text4 = "オフ"
            #print(self.text4)

        elif self.text4 == "オフ":
            self.text4 = "オン"
            #print(self.text4)

    def tempUpdate(self):
        if (RASPBERRY_CODE  == True):
            self.temp_now = str(pt100.pt100GetTmp())
        

    def btc2(self): #UP  
        global glob_setting_temp

        if('Mouse' in glob_event_type):
            self.set_num = self.set_num + 1
            if (self.set_num > 10):
                self.set_num = 10
            self.temp_set  = str(self.set_num)
            glob_setting_temp = self.set_num
            # print("#DEBUG set TEMP push Plus:"  , self.set_num) 
            # print("#DEBUG set grobal_setting_temp:"  , glob_setting_temp) 


    def btc3(self):  
        global glob_setting_temp

        if('Mouse' in glob_event_type):
            self.set_num = self.set_num - 1

            if (self.set_num < -35):
                self.set_num = -35

            self.temp_set  = str(self.set_num)
            glob_setting_temp = self.set_num
            # print("#DEBUG set TEMP push minus:"  , self.set_num) 
            # print("#DEBUG set grobal_setting_temp:"  , glob_setting_temp) 

class Display(Screen):
    ev_type = ''
    
    def touch_down_def(self, touch):
        global glob_event_type

        glob_event_type = str(type(touch))
        ev_type = glob_event_type
        print(ev_type)
    pass

class SM02App(App):
    smpy = ScreenManager() 
    #err_flag = 0;

    def err_occur_trans(self):
        #if (self.err_flag == 1):
        if GPIO.input(12) == 1:
            self.smpy.current= 'Screen_Alert'

    def build(self):
        #Clock.schedule_interval(lambda dt: control_OnOff_by_temp(), glob_delay*60)
        Clock.schedule_interval(lambda dt: control_OnOff_by_temp(), 2)
        Clock.schedule_interval(lambda dt: Err_and_Bzr(), 1)
        self.smpy.add_widget(Display(name='Display'))
        self.smpy.add_widget(Screen_Alert(name='Screen_Alert'))
        self.smpy.add_widget(Screen_One(name='Screen_One'))
        self.smpy.current = 'Display'
        Clock.schedule_interval(lambda dt: self.err_occur_trans(), 5)
        #return Display()
        return self.smpy

if __name__ == "__main__":
    SM02App().run()
