import multiprocessing
import os                                                                       
from multiprocessing import Pool

processes = ('Identification/faceRecognition.py', 'SpeechRecognizer/speechRecognition.py') 

def run_process(process):                                                             
    os.system('python {}'.format(process) + '&')                                       
                                                                                
                                                                                
pool = Pool(processes=2)                                                        
pool.map(run_process, processes)    
