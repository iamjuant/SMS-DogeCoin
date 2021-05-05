import unittest
from selenium import webdriver
import time
import math
from twilio.rest import Client
from var import twilioAuth

class NewUser(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome(executable_path = r'C:\\Users\\jtruj\\OneDrive\\Desktop\\Pranks\\SMS-DogeCoin\\chromedriver_win32\\chromedriver.exe')
        driver=self.driver  
        driver.get('https://robinhood.com/crypto/DOGE')
        driver.minimize_window()
        self.flag = 'GO'

        self.user = {
           'dAverageCost': self.getCurrentPrice(), #the average cost that you bought all your dogecoins
           'initialDesiredPercentageChange':0.2, #percentage that the assistant will use to send first sms
           'percentageChangeAfter':0.4, #percentage after the first sms ex. first is 2% and this one is 0.5, so you will receive a message at 2%, 2.5% 3%... or in a negative way
        }
    def updateUser(self):
        account_sid=twilioAuth['account_sid']
        auth_token=twilioAuth['auth_token']
        client = Client(account_sid, auth_token)
        user= self.user
        index = 0
        #this loop is in case we have the trial account on twilio
        for i in range(len(client.messages.list())):
            if client.messages.list()[i].body.startswith('Sent'):
                pass
            else:
                index = i
                break
        lastMessage = client.messages.list()[index].body.split(',') #dAverageCost
        if user['dAverageCost']!= float(lastMessage[0]):
            user['dAverageCost']=float(lastMessage[0])
            user['initialDesiredPercentageChange']=float(lastMessage[1])
            user['percentageChangeAfter'] = float(lastMessage[2])
            self.flag = 'GO'
            

    def getCurrentPrice(self):
        driver = self.driver     
        dogecoin =driver.find_elements_by_xpath('/html/body/div[1]/main/div[3]/div/div/div/div/div/div/div/div[2]/div/div[1]/div[2]/form/div[1]/div[1]/div[1]/div[2]/div[2]/span')
        # dogecoin = float(driver.find_element_by_xpath('/html/body/div/div/div[2]/div/div[1]/div[2]/div[2]/div[1]/div').text[1:].strip())
        doge = float(dogecoin[0].text[1:])
        return doge
    def sendSMS(self,message):
        account_sid=twilioAuth['account_sid']
        auth_token=twilioAuth['auth_token']
        client = Client(account_sid, auth_token)
        #we send the sms to the cellphone
        client.messages.create(
                body=message,
                to= twilioAuth['to'],
                from_=twilioAuth['from_']
            )
    def test_new_user(self):
        user=self.user
        while(True):
            #We have to get the current price for dogecoin 
            dogecoin = self.getCurrentPrice()
            print(f'The price to watch is { user["dAverageCost"] } ')
            print('Current dogecoin is: ',dogecoin)
            #We get the percentage change for what we have
            percentage = (dogecoin/user['dAverageCost'])-1 #this operation will give the +/- percentage change
            print(f'The percentage change is {round(percentage,3)} \n')

            if  percentage > self.user['initialDesiredPercentageChange'] and self.flag=='GO': 
                #send SMS 
                message=f'The Percentage change is more than {user["initialDesiredPercentageChange"]}% time to check DOGECOIN!! \n Sending SMS \n'
                print(message)
                # self.sendSMS(message)
                self.flag='STOP'

            elif percentage < -user['initialDesiredPercentageChange'] and self.flag == 'GO':
                message = f'The Percentage change is less than {user["initialDesiredPercentageChange"]}% time to check DOGECOIN!! \n Sending SMS \n'
                # self.sendSMS(message)
                print(message)
                self.flag = 'STOP'
            else: # If it is between the range just pass
                pass
            #we update the user just in case he sends new parameters through sms
            self.updateUser()
            time.sleep(5) #we sleep the loop for some seconds 
    def tearDown(self):
        time.sleep(1.0)
        self.driver.quit()

if __name__ == "__main__":
    unittest.main(verbosity=2, warnings='ignore')
    