import threading
import time

class FacialRecognition(threading.Thread):
    def run(self):
        print("{} started1".format(self.getName()))
        time.sleep(1)
        print("{} finished!".format(self.getName()))
def main():
    for x in range(4):
        frThread = FacialRecognition(name = "Facial Recognizer".format(x + 1))
        frThread.start()
        time.sleep(.9)

if __name__== '__main__':main()
