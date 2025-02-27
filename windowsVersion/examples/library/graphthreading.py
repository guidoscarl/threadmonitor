# coding=utf-8

from threading import Lock,Condition
from threading import current_thread
from time import sleep
from tkinter import ttk
from tkinter import *
import tkinter
from threading import Lock,Thread
from PIL import ImageTk
import os
import threading
import time
from functools import partial




class ConditionContainer:
    def __init__(self,conditionContainer,image,containerHeight,imageComputerHeight,imageComputerWidth,semCanvas,conditionLabel,semGreenCanvas):
        self.container = conditionContainer
        self.lock = Lock()
        self.conditionThreads = []
        self.currentWidth = 20
        self.image = image
        self.containerHeight = containerHeight
        self.imageComputerHeight=imageComputerHeight
        self.imageComputerWidth = imageComputerWidth
        self.semCanvas = semCanvas
        self.conditionLabel = conditionLabel
        self.semGreenCanvas=semGreenCanvas

    def setConditionLabel(self,name):
        self.conditionLabel.configure(text=name)

    def addThreadInCondition(self,thread):
        with self.lock:
            self.conditionThreads.append(thread)
            self.drawNewThread(thread)

    def removeThreadInCondition(self,threadObject):
        with self.lock:
            if threadObject in self.conditionThreads:
                for thread in self.conditionThreads:
                    self.container.delete('image'+str(thread.ident))
                    self.container.delete('text'+str(thread.ident))
                self.conditionThreads.remove(threadObject)
                self.redrawThread()
    
    def redrawThread(self):
        currentWidth = 20
        imageHeight = 0 


        for thread in self.conditionThreads:
            tag=str(thread.ident)
            self.container.create_image(currentWidth,imageHeight,image=self.image,tag='image'+tag,anchor='n')
            self.container.create_text(currentWidth,imageHeight+(100/100)*self.imageComputerHeight,text=thread.getName(),tag='text'+tag,anchor="n")
            currentWidth+=self.imageComputerWidth*2
        self.currentWidth=currentWidth
    
    def drawNewThread(self,thread):
        tag = str(thread.ident)
        imageHeight = 0
        self.container.create_image(self.currentWidth,imageHeight,image=self.image,tag='image'+tag,anchor='n')
        self.container.create_text(self.currentWidth,imageHeight+(100/100)*self.imageComputerHeight,text=thread.getName(),tag='text'+tag,anchor="n",font="Times 10 ")
        self.currentWidth+=self.imageComputerWidth*2
    def blinkCondition(self,startTime,red,grey):
        updateCanvas = self.semCanvas if grey == "greyRedSem" else self.semGreenCanvas
        currentTime = time.time()
        if currentTime<=startTime+7:
            state = "hidden" if red else "normal"
            updateCanvas.itemconfigure(grey,state=state)
            updateCanvas.after(400,self.blinkCondition,startTime,not red,grey)
        else:
            updateCanvas.itemconfigure(grey,state='normal')
class _InactiveContainer:
    def __init__(self,inactiveContainer,image):
        self.container = inactiveContainer
        self.lock = Lock()
        self.inactiveThreads = []
        self.currentWidth = 0
        self.image = image

    def addThreadInactive(self,thread,lock):
        with self.lock:
            self.inactiveThreads.append(thread)
            self.drawNewThread(thread,lock)

    def removeThreadInactive(self,threadObject):
        with self.lock:
            if threadObject in self.inactiveThreads:
                for thread in self.inactiveThreads:
                    self.container.delete('image'+str(thread.ident))
                    self.container.delete('text'+str(thread.ident))
                self.inactiveThreads.remove(threadObject)
                self.redrawThread()
    
    def redrawThread(self):
        currentWidth = 0
        

        for thread in self.inactiveThreads:
            tag=str(thread.ident)
            self.container.create_image(currentWidth,30,image=self.image,tag='image'+tag,anchor='n')
            self.container.create_text(currentWidth,100,text=thread.getName(),tag='text'+tag,anchor="n")
            currentWidth+=100
        self.currentWidth=currentWidth
    
    def drawNewThread(self,thread,lock):
        lock.releaseLock.acquire()
        tag = str(thread.ident)
        self.container.create_image(self.currentWidth,30,image=self.image,tag='image'+tag,anchor='n')
        self.container.create_text(self.currentWidth,100,text=thread.getName(),tag='text'+tag,anchor="n")
        self.currentWidth +=100
        lock.releaseCondition.notify_all()
        lock.isReleased=True
        lock.releaseLock.release()



class _WaitContainer:
    def __init__(self,wait_container,image,imageHeight):
        self.container = wait_container
        self.lock = Lock()
        self.waitThreads = []
        self.currentHeight = 0
        self.image = image
        self.imageHeight = imageHeight
    
    def addThreadInWait(self,thread,lock):
        with self.lock:
            self.waitThreads.append(thread)
            self.drawNewThread(thread)
            lock.canAquire=True

    def removeThreadInWait(self,threadObject):
        with self.lock:
            for thread in self.waitThreads:
                tag = str(thread.ident)
                self.container.delete('text'+tag)
                
                self.container.delete('image'+str(thread.ident))

            self.waitThreads.remove(threadObject)
            self.redrawThread()
    
    def redrawThread(self):
        currentHeight = 0
        

        for thread in self.waitThreads:
            tag=str(thread.ident)
            self.container.create_image(int(self.container.winfo_width()/2),currentHeight,image=self.image,tag='image'+tag,anchor='n')
            currentHeight+=1.2*self.imageHeight
            self.container.create_text(int(self.container.winfo_width()/2),currentHeight,text=thread.getName(),tag='text'+tag,anchor="n")
            currentHeight+=0.5*self.imageHeight
        self.currentHeight=currentHeight
    
    def drawNewThread(self,thread):
        tag = str(thread.ident)
        self.container.create_image(int(self.container.winfo_width()/2),self.currentHeight,image=self.image,tag='image'+tag,anchor='n')
        self.currentHeight+=1.2*self.imageHeight
        self.container.create_text(int(self.container.winfo_width()/2),self.currentHeight,text=thread.getName(),tag='text'+tag,anchor="n")
        self.currentHeight +=0.5*self.imageHeight

    def drawFutureAcquireThread(self,thread):
        self.container.itemconfigure('text'+str(thread.ident),fill='#cd5b45')
            
            

class _modifyLockNameWindow:
    def __init__(self,lock):
        pass
class Controller:
    FINISH=False
    DESTRA = 1
    SINISTRA = 0
    INDEX_WAIT_CONTAINER = 1
    INDEX_LOCK_CONTAINER = 1
    isStopped = False
    
    
    def __init__(self,stepLock,stepCondition):
        
        self.window=Tk()
        self.stepLock=stepLock
        self.stepCondition = stepCondition

        self.screen_width=self.window.winfo_screenwidth()
        self.screen_heigth=self.window.winfo_screenheight()
        self.pad = 3
        self.window.geometry('{0}x{1}'.format(self.screen_width-self.pad,self.screen_heigth-self.pad))
        self.started = False
        self.step = 0
        ### INIZIALIZZAZIONE LOGICA ###

        ### hashMap contenente come chiave il nome del lock, e come valore il relativo canvas ###
        self.lockContainer={}
        
        ### In quale container è conenuto al momento il thread ###
        self.threadContainer = {}

        ### wait container associato a uno specifico lock ###
        self.waitContainer = {}

        ### Lista dei threads ###
        self.threads = []

        ### Lista dei thread inattivi ###
        self.inactiveThread=[]

        ### Lista dei thread in wait su un determinato lock ###
        self.waitThread = {}

        ### PUNTI DI PARTENZA DEI CONTAINERS ###
        self.currentOrientPosition = 0
        self.currentHeightPosition = 200
        
        self.containerWidth = self.screen_width/5
        self.containerHeight = 200
        self.conditionHeight=(40/100)*self.containerHeight
        self.waitHeight = (30/100)*self.containerHeight
        self.lockHeight = (70/100)*self.containerHeight
        self.inactiveWidth = 500

        self.releasingLock = []
       
        ### Lista di tutti i container creati ###
        self.containers = []

        ### Contiene come chiave gli scroll, e come valore gli oggetti a cui sono attaccati ###
        self.scrolls = []

        self.conditions = []
       
        ### Inizializzazione inactive Frame ###
        
        #self.inactiveFrame=Frame(self.window,background='#ff1a1a')
        #self.inactiveFrame.pack(fill=BOTH)
        

        ### Inizializzazione primaryCanvas ###

        self.frame=Frame(self.window,width=self.screen_width,height = self.screen_heigth,background='grey')
        self.frame.pack(fill=BOTH,expand=True)
        self.primaryCanvas=Canvas(self.frame,background='#A0A0A0',highlightthickness=0, highlightbackground="black",height=10000,width=self.screen_width)
        self.window.update_idletasks()
        self.yscroll = Scrollbar(self.frame, orient=VERTICAL)
        self.yscroll['command']= self.primaryCanvas.yview
        self.yscroll.pack(side=RIGHT,fill=Y)
        self.primaryCanvas['yscrollcommand']= self.yscroll.set
        self.primaryCanvas.pack(fill=BOTH,expand=True)

        self.inactiveCanvas=Canvas(self.primaryCanvas,background='white',highlightthickness=1, highlightbackground="black",height=150,width=self.inactiveWidth)
        changeThreadButton = Button(self.inactiveCanvas,text = "Change thread name", command=self.createPopupThread)
        changeThreadButton.place(relx=0.5,rely=0,anchor='n')
        self.inactiveScroll = ttk.Scrollbar(self.inactiveCanvas,orient=HORIZONTAL,command=self.inactiveCanvas.xview)
        self.inactiveScroll.place(relx=0.5,rely=0.93,width=305,anchor='center')
        self.inactiveCanvas.configure(xscrollcommand=self.inactiveScroll.set)
        #self.inactiveCanvas.pack(anchor='center',pady=10)
        self.background = ImageTk.Image.open('resource/background.jpg')
        self.background = self.background.resize((10000,self.screen_width))
        self.background = ImageTk.PhotoImage(master=self.primaryCanvas,image=self.background)
        #self.primaryCanvas.create_image(0,0,image=self.background,anchor='n')

        self.primaryCanvas.create_window(self.screen_width/2,0,window=self.inactiveCanvas,anchor='n')

        self.playButton = Button(self.primaryCanvas,text='play',command=self.play)
        self.stopButton = Button(self.primaryCanvas,text='pause',command=self.stop)
        self.nextStepButton = Button(self.primaryCanvas,text='next step',command=self.nextStep,state='disabled')

        self.playButton.place(relx=0.93,rely=0.02)
        self.stopButton.place(relx=0.93,rely=0.04)
        self.nextStepButton.place(relx=0.93,rely=0.06)

        ### Inizializzazioni immagini ###
        self.imageComputerHeight = 32
        self.imageComputerWidth = 32
        self.computerImage = ImageTk.Image.open('resource/computer.png')
        self.computerImage = self.computerImage.resize((self.imageComputerHeight,self.imageComputerHeight))
        self.computerImage = ImageTk.PhotoImage(master=self.primaryCanvas,image=self.computerImage)
        

        self.redSem = ImageTk.Image.open('resource/redSem.png')
        self.redSem = self.redSem.resize((15,15))
        self.redSem = ImageTk.PhotoImage(master=self.primaryCanvas,image=self.redSem)

        self.greenSem = ImageTk.Image.open('resource/greenSem.png')
        self.greenSem = self.greenSem.resize((15,15))
        self.greenSem = ImageTk.PhotoImage(master=self.primaryCanvas,image=self.greenSem)

        self.greySem = ImageTk.Image.open('resource/greySem.png')
        self.greySem = self.greySem.resize((15,15))
        self.greySem = ImageTk.PhotoImage(master=self.primaryCanvas,image=self.greySem)
       
        self.window.after(50,self.update)
        self.window.protocol('WM_DELETE_WINDOW',self.__onclose)
        
        self.inactiveData = _InactiveContainer(self.inactiveCanvas,self.computerImage)

    def play(self):
        with self.stepLock:
            self.stopButton.configure(state='normal')
            self.nextStepButton.configure(state='disabled')
            self.isStopped=False
            self.primaryCanvas.configure(background='#A0A0A0')
            for lock in self.lockContainer.keys():
                lock.playController.play()
            self.step=0          
            self.stepCondition.notifyAll()
    
    def stop(self):
        self.playButton.configure(state='normal')
        self.nextStepButton.configure(state='normal')
        self.isStopped=True
        self.primaryCanvas.configure(background='#696969')
        for lock in self.lockContainer.keys():
            lock.playController.stop()
    
    def nextStep(self):
        with self.stepLock:
            self.step+=1
            self.stepCondition.notifyAll()
    
    def decreaseStep(self):
        self.step-=1
    def changeThreadName(self,label,textField,menu,button):
        threads={}
        for thread in self.threads:
            threads[thread.getName()]=thread
        threads[label['text']].name=textField.get('1.0','end-1c')
        label.configure(text='Name modified!')
        menu.delete(0,len(self.threads)-1)
        for thread in self.threads:
            calling_data = partial(self.setLabel,label,thread.getName(),textField,button)
            menu.add_command(label=thread.getName(),command= calling_data)
        button.configure(state='disabled')
        textField.configure(state='disabled')

        
    def createPopupThread(self):
        popup = Toplevel()
        popup.title('Change thread name')
        popup.geometry('400x200')
        menu = Menu(popup)
        popup.config(menu=menu)
        threadBar = Menu(menu,tearoff=0)
        label=Label(popup,text='')
        label.place(rely=0.25,relx=0.5,anchor='n')
        textField = Text(popup,state='disabled')
        textField.place(relx=0.5,rely=0.40,relheight=0.2,relwidth=0.5,anchor='n')
        changeThreadNameData=partial(self.changeThreadName,label,textField,threadBar)      
        button = Button(popup,text='Change name')
        changeThreadNameData=partial(self.changeThreadName,label,textField,threadBar,button)
        button.configure(command= changeThreadNameData)
        button.place(relx=0.5,rely=1,anchor='s')
        for thread in self.threads:
            calling_data = partial(self.setLabel,label,thread.getName(),textField,button)
            threadBar.add_command(label=thread.getName(),command= calling_data)
        menu.add_cascade(label='Select thread',menu=threadBar)       
        popup.mainloop()

    def setLabel(self,label,text,textField,button):
        label.configure(text=text)
        textField.configure(state="normal")
        button.configure(state="normal")
    def createPopupLock(self,label):
        popup = Toplevel()
        popup.title(label['text'])
        popup.geometry('400x100')
        textField = Text(popup)
        textField.place(relx=0,rely=0,relheight=0.5,relwidth=1)
        button = Button(popup,text='Change name',command= lambda: (label.configure(text=textField.get('1.0','end-1c'))))
        button.place(relx=0.5,rely=1,anchor='s')
        popup.mainloop()

    def addThread(self,thread):
        self.threads.append(thread)
    def setLockName(self,lock,name):
        lock_data =self.lockContainer[lock]
        lock_label = lock_data[5]
        lock_label.configure(text=name)
    def addLock(self,lock):
        ### creo il container e lo aggiungo alla lista di container ###
        
        container=Canvas(self.primaryCanvas,background='white',highlightthickness=1, highlightbackground="black",height=self.containerHeight,width=self.containerWidth)
        
        
        self.containers.append(container)

        
        
        ### creo il container che mostra il thread che ha acquisito il lok ###
        lock_container = Canvas(container,background='white',width = self.containerWidth, height=self.lockHeight)
        lockLabel = Label(lock_container,text = 'Lock '+str(lock.getId()))
        lockLabel.place(relx=0.5,rely=0.80,anchor='center')
        container.create_window(self.containerWidth/2,(30/100)*self.containerHeight,window=lock_container,anchor='n')
        
        ### creo il container che mostra i thread in wait ###
        waitContainer= Canvas(container,background='#fff7dc',highlightthickness=1, highlightbackground="black",width=self.containerWidth,height=self.waitHeight)
        container.create_window(self.containerWidth/2,(0/100)*self.containerHeight,window=waitContainer,anchor='n')#.place(relx=0.5,anchor='center',rely=0.25, relheight=0.50,relwidth=1)
        waitLabel = Label(waitContainer,text='Wait threads')
        waitLabel.place(relx=0,rely=0,anchor='nw')
        self.waitContainer[lock]=waitContainer

        ### creo i semafori che mostrano lo stato attuale del lock ###
        lock_container.create_image(self.containerWidth*(90/100),self.containerHeight*(50/100),image=self.redSem, tag="redSem",state="hidden")
        lock_container.create_image(self.containerWidth*(90/100),self.containerHeight*(50/100),image=self.greySem, tag="greyRedSem")

        lock_container.create_image(self.containerWidth*(90/100),self.containerHeight*(60/100),image=self.greenSem, tag="greenSem")
        lock_container.create_image(self.containerWidth*(90/100),self.containerHeight*(60/100),image=self.greySem, tag="greyGreenSem",state="hidden")


        
        
        ### creo lo scroll del canvas per i thread in wait ###
        scroll = Scrollbar(waitContainer,orient=VERTICAL,command=waitContainer.yview)
        scroll.place(relx=1,rely=0.5,relheight=1,anchor='e')
        waitContainer.configure(yscrollcommand=scroll.set)
        self.scrolls.append(scroll)
        
        wait_data = _WaitContainer(waitContainer,self.computerImage,self.imageComputerHeight)

        
        ### associo al lock i relativi container ###
        conditionContainers = {}
        currentHeightCanvas = self.containerHeight
        self.lockContainer[lock]=[lock_container,wait_data,conditionContainers,self.currentHeightPosition,self.currentOrientPosition%2,lockLabel,currentHeightCanvas,container]
        
        ### aggiorno le variabili per il posizionamento ###
        self.currentOrientPosition+=1
        
    def addCondition(self,condition,lock):
        ### prendo il container principale del lock a cui è associata la condition ###
        container_data = self.lockContainer[lock]
        lock_container=container_data[7]

        ### prendo i dati utili a creare la window per la condition ###
        current_height = container_data[6]
        current_height+=self.conditionHeight
        container_data[6]=current_height
        lock_container.configure(height=current_height)

        ### prendo il container delle condition associate al lock ###
        conditionContainers = container_data[2]

        ### creo il canvas relativo alla condition che sto aggiungendo ###
        conditionContainer = Canvas(lock_container,background='#ffc04c',highlightthickness=1, highlightbackground="black",width=self.containerWidth,height=self.conditionHeight)
        lock_container.create_window(self.containerWidth/2,(100/100)*current_height,window=conditionContainer,anchor='s')
        semCanvas = Canvas(lock_container,background='#ffc04c',width=60,height=17)
        lock_container.create_window(self.containerWidth*(80/100),current_height-(45/100)*self.conditionHeight,window=semCanvas,anchor='n')
        semCanvas.create_image(15,10,image=self.redSem, tag="redSem",anchor='center')
        semCanvas.create_image(15,10,image=self.greySem, tag="greyRedSem",anchor='center')
        semCanvas.create_text(45,12,text="UNO")

        semGreenCanvas = Canvas(lock_container,background='#ffc04c',width=60,height=17)
        lock_container.create_window(self.containerWidth*(20/100),current_height-(45/100)*self.conditionHeight,window=semGreenCanvas,anchor='n')
        semGreenCanvas.create_image(45,10,image=self.greenSem, tag="greenSem",anchor='center')
        semGreenCanvas.create_image(45,10,image=self.greySem, tag="greyGreenSem",anchor='center')
        semGreenCanvas.create_text(15,12,text="ALL")


        conditionLabel = Label(conditionContainer,text='Condition '+condition.name)
        conditionLabel.place(relx=0.5,rely=0.70,anchor='c')
        scroll = Scrollbar(conditionContainer,orient=HORIZONTAL,command=conditionContainer.xview)
        scroll.place(relx=0,rely=1,relwidth=1,anchor='sw')
        conditionContainer.configure(xscrollcommand=scroll.set)
        conditionData = ConditionContainer(conditionContainer,self.computerImage,self.conditionHeight,self.imageComputerHeight,self.imageComputerWidth,semCanvas,conditionLabel,semGreenCanvas)
        ### inserisco la condition nel container ###
        conditionContainers[condition]=conditionData
        self.conditions.append(conditionContainer)

    def setConditionName(self,condition,lock,name):
        lock_data=self.lockContainer[lock]
        conditionContainer = lock_data[2]
        conditionContainer[condition].setConditionLabel(name)
    def __moveFromInactiveToWait(self,thread,wait_container,height,orient,tag,lock,startTime):
       
        if self.primaryCanvas.coords(tag)[1]<=height-(10/100)*self.containerHeight:
            self.primaryCanvas.move('image'+str(thread.ident),0,2)
            self.primaryCanvas.move(tag,0,2)
            self.primaryCanvas.after(6,self.__moveFromInactiveToWait,thread,wait_container,height,orient,tag,lock,startTime)

                
        else:
            if orient == Controller.SINISTRA:
                if self.primaryCanvas.coords(tag)[0]>=((30/100)*self.primaryCanvas.winfo_width()):
                    self.primaryCanvas.move(tag,-2,0)
                    self.primaryCanvas.move('image'+str(thread.ident),-2,0)
                    self.primaryCanvas.after(10,self.__moveFromInactiveToWait,thread,wait_container,height,orient,tag,lock,startTime)
                else:
                    wait_container.addThreadInWait(thread,lock)
                    self.primaryCanvas.delete(tag)
                    self.primaryCanvas.delete('image'+str(thread.ident))


            else:
                if self.primaryCanvas.coords(tag)[0]<=((70/100)*self.primaryCanvas.winfo_width()):
                    self.primaryCanvas.move(tag,2,0)
                    self.primaryCanvas.move('image'+str(thread.ident),2,0)
                    self.primaryCanvas.after(10,self.__moveFromInactiveToWait,thread,wait_container,height,orient,tag,lock,startTime)
                else:
                    wait_container.addThreadInWait(thread,lock)
                    lock.canAcquire=True
                    self.primaryCanvas.delete(tag)
                    self.primaryCanvas.delete('image'+str(thread.ident))

    def __moveInLock(self,tagImage, tagText,orient,container,lock,thread,tag,alreadyCalled):
        if orient == controller.SINISTRA:
            if container.coords(tagImage)[0]>0:
                if container.coords(tagImage)[0]<16:
                    if not alreadyCalled:
                        self.__moveFromLockToInactive(tag,thread,orient,lock,container)
                        alreadyCalled = True

                container.move(tagImage,-1,0)
                container.move(tagText,-1,0)
                container.after(2,self.__moveInLock,tagImage, tagText, orient,container,lock,thread,tag,alreadyCalled)
            else:
                container.delete(tagImage)
                container.delete(tagText)
        else:
            if container.coords(tagImage)[0]<self.containerWidth:
                if container.coords(tagImage)[0]>self.containerWidth-32:
                    if not alreadyCalled:
                        self.__moveFromLockToInactive(tag,thread,orient,lock,container)
                        alreadyCalled = True

                container.move(tagImage,1,0)
                container.move(tagText,1,0)
                container.after(4,self.__moveInLock,tagImage, tagText, orient,container,lock,thread,tag,alreadyCalled)
            else:
                container.delete(tagImage)
                container.delete(tagText)
                

    def __moveFromLockToInactive(self,tag,thread,orient,lock,container):
        
        if orient == Controller.SINISTRA and  self.primaryCanvas.coords('inactiveimage'+str(thread.ident))[0]>(5/100)*self.primaryCanvas.winfo_width() and self.primaryCanvas.coords('inactiveimage'+str(thread.ident))[1]>0:
            self.primaryCanvas.move(tag,-1,0)
            self.primaryCanvas.move('inactiveimage'+str(thread.ident),-1,0)
            self.primaryCanvas.after(2,self.__moveFromLockToInactive,tag,thread,orient,lock,container)
        elif orient == Controller.DESTRA and  self.primaryCanvas.coords('inactiveimage'+str(thread.ident))[0]<(95/100)*self.primaryCanvas.winfo_width() and self.primaryCanvas.coords('inactiveimage'+str(thread.ident))[1]>0:
            self.primaryCanvas.move(tag,1,0)
            self.primaryCanvas.move('inactiveimage'+str(thread.ident),1,0)
            self.primaryCanvas.after(2,self.__moveFromLockToInactive,tag,thread,orient,lock,container)
        else:
            if self.primaryCanvas.coords('inactiveimage'+str(thread.ident))[1]>0:
                self.primaryCanvas.move(tag,0,-3)
                self.primaryCanvas.move('inactiveimage'+str(thread.ident),0,-3)
                self.primaryCanvas.after(12,self.__moveFromLockToInactive,tag,thread,orient,lock,container)
            else:
                if orient == Controller.DESTRA and self.primaryCanvas.coords('inactiveimage'+str(thread.ident))[0]>=((50/100)*self.screen_width)+((50/100)*self.inactiveWidth):# and (self.primaryCanvas.coords('inactiveimage'+thread)[0]<=(50/100)*self.screen_width):                    self.primaryCanvas.move(tag,1,0)
                    self.primaryCanvas.move('inactiveimage'+str(thread.ident),-2,0)
                    self.primaryCanvas.move(tag,-2,0)
                    self.primaryCanvas.after(10,self.__moveFromLockToInactive,tag,thread,orient,lock,container)
                elif orient == Controller.SINISTRA and self.primaryCanvas.coords('inactiveimage'+str(thread.ident))[0]<=((50/100)*self.screen_width)-((50/100)*self.inactiveWidth):# and self.primaryCanvas.coords('inactiveimage'+thread)[0]>=(50/100)*self.screen_width:                    self.primaryCanvas.move(tag,1,0)
                    self.primaryCanvas.move('inactiveimage'+str(thread.ident),2,0)
                    self.primaryCanvas.move(tag,2,0)
                    self.primaryCanvas.after(10,self.__moveFromLockToInactive,tag,thread,orient,lock,container)
                else:
                    self.primaryCanvas.delete(tag)
                    self.primaryCanvas.delete('inactiveimage'+str(thread.ident))
                    self.inactiveData.addThreadInactive(thread,lock)
                    self.releasingLock.remove(lock)
                    container.itemconfigure('greyRedSem',state='normal')         
                    container.itemconfigure('greyGreenSem',state="hidden")
                    


    def setWaitThread(self,thread,lock):
        container_data = self.lockContainer[lock]
        wait_data = container_data[1]  
        height = container_data[3]+((30/100)*self.containerHeight)
        orient = container_data[4]
        tag="wait"+str(thread.ident)+str(lock.getId())
        self.primaryCanvas.create_text(int(self.primaryCanvas.winfo_width()/2),(105/100)*self.imageComputerHeight,text=thread.getName(),tag=tag,anchor="n")
        self.primaryCanvas.create_image(int(self.primaryCanvas.winfo_width()/2),0,image=self.computerImage,tag='image'+str(thread.ident),anchor='n')
        timeStart = time.time()
        self.__moveFromInactiveToWait(thread,wait_data,height,orient,tag,lock,timeStart)
        self.inactiveData.removeThreadInactive(thread)
        sleepTime = (height+(self.primaryCanvas.winfo_width()/2)-((30/100)*self.primaryCanvas.winfo_width()))/100 
        return sleepTime
    
    def setAcquireThread(self,thread,lock):
        container_data = self.lockContainer[lock]
        lock_container = container_data[0]
        tag=str(thread.ident)
        wait_container = container_data[1]
        wait_container.removeThreadInWait(thread)
        imageHeight = (25/100)*self.lockHeight
        lock_container.create_image((50/100)*self.containerWidth,imageHeight,tag = 'acquireImage'+tag,image=self.computerImage,anchor='n')
        lock_container.create_text((50/100)*self.containerWidth,imageHeight+(1.2*self.imageComputerHeight),text=thread.getName(),tag='text'+tag,anchor='n',fill='green')
        lock_container.itemconfigure('greyGreenSem',state="normal")
        lock_container.itemconfigure('greyRedSem',state="hidden")
        lock_container.itemconfigure('redSem',state="normal")
    
    def setAcquireThreadFromCondition(self,thread,lock,condition):
        tag=str(thread.ident)
        container_data = self.lockContainer[lock]
        conditionContainer =container_data[2]
        conditionData = conditionContainer[condition]
        conditionData.removeThreadInCondition(thread)
        imageHeight = (25/100)*self.lockHeight
        lock_container = container_data[0]
        lock_container.create_image((50/100)*self.containerWidth,imageHeight,tag = 'acquireImage'+tag,image=self.computerImage,anchor='n')
        lock_container.create_text((50/100)*self.containerWidth,imageHeight+(1.2*self.imageComputerHeight),text=thread.getName(),tag='text'+tag,anchor='n',fill='green')
        lock_container.itemconfigure('greyGreenSem',state="normal")
        lock_container.itemconfigure('greyRedSem',state="hidden")
        lock_container.itemconfigure('redSem',state="normal")
    

    def setThreadInCondition(self,thread,lock,condition):
        container_data = self.lockContainer[lock]
        conditionContainers =container_data[2]
        conditionData = conditionContainers[condition]
        conditionData.addThreadInCondition(thread)
        lock_container=container_data[0]
        lock_container.delete('text'+str(thread.ident))
        lock_container.delete('acquireImage'+str(thread.ident))
        lock_container.itemconfigure('greyRedSem',state='normal')         
        lock_container.itemconfigure('greyGreenSem',state="hidden")
        sleep(2)

    def setReleaseThread(self,thread,lock):
        container_data = self.lockContainer[lock]
        lock_container=container_data[0]
        height = container_data[3]+((50/100)*self.containerHeight)
        orient = container_data[4]
        tagImage = 'acquireImage'+str(thread.ident)
        tagText = 'text'+str(thread.ident)
        
        tag = "release"+str(thread.ident)
        
        if orient== Controller.SINISTRA:
            self.primaryCanvas.create_image((12/100)*self.primaryCanvas.winfo_width(),height,tag = 'inactiveimage'+str(thread.ident),image=self.computerImage,anchor='n')
            self.primaryCanvas.create_text((12/100)*self.primaryCanvas.winfo_width(),height+(1.2*self.imageComputerHeight),text = thread.getName(),tag=tag,anchor='n')
        else:
            self.primaryCanvas.create_image((88/100)*self.primaryCanvas.winfo_width(),height,tag = 'inactiveimage'+str(thread.ident),image=self.computerImage,anchor='n')
            self.primaryCanvas.create_text((88/100)*self.primaryCanvas.winfo_width(),height+(1.2*self.imageComputerHeight),text = thread.getName(),tag=tag,anchor='n')
        self.__moveInLock(tagImage, tagText, orient,lock_container,lock,thread,tag,False)
        lock_container.itemconfigure('greyRedSem',state="normal")
        self.releasingLock.append(lock)
        lock_container.after(500,self.__blinkLock,lock_container,True,lock)
        sleepTime = (height+(self.primaryCanvas.winfo_width()/2)-((30/100)*self.primaryCanvas.winfo_width()))/80
        return sleepTime
        
    def drawFutureLockThread(self,thread,lock):
        container_data = self.lockContainer[lock]
        wait_data= container_data[1]
        wait_data.drawFutureAcquireThread(thread)

    def notifyLock(self,lock,condition,isAll):
        container_data = self.lockContainer[lock]
        conditionContainer = container_data[2]
        conditionData = conditionContainer[condition]
        startTime = time.time()
        red = True
        grey = "greyRedSem" if not isAll else "greyGreenSem"
        conditionData.blinkCondition(startTime,red,grey)
    
    def __blinkCondition(self,container,startTime,red):
        currentTime = time.time()
        if currentTime<=startTime+7:
            state = "hidden" if red else "normal"
            container.itemconfigure('greyRedSem',state=state)
            container.after(400,self.__blinkCondition,container,startTime,not red)
        else:
            container.itemconfigure('greyRedSem',state='normal')

    def __blinkLock(self,container,currentState,lock):
        if lock in self.releasingLock:
            state = 'normal' if currentState else 'hidden'
            container.itemconfigure('greyRedSem',state=state) 
            container.after(500,self.__blinkLock,container, not currentState,lock)
        
            
    def update(self):
        self.primaryCanvas.configure(scrollregion=self.primaryCanvas.bbox("all"))
        self.inactiveCanvas.configure(scrollregion=self.inactiveCanvas.bbox("all")) 
        for key in self.waitContainer.keys():
            self.waitContainer[key].configure(scrollregion=self.waitContainer[key].bbox("all"))
        for container in self.conditions:
            container.configure(scrollregion=container.bbox("all"))
        self.window.after(50,self.update)
    
    def start(self):
        for key in self.lockContainer.keys():
            containerData=self.lockContainer[key]
            container = containerData[7]
            currentOrient=containerData[4]

            relX = (20/100)*self.screen_width if currentOrient%2 == 0 else (80/100)*self.screen_width
            self.primaryCanvas.create_window(relX,self.currentHeightPosition,window=container,anchor='n')
            containerData[3]=self.currentHeightPosition
            if(currentOrient%2 != 0):
                self.currentHeightPosition+=containerData[6]+30
        self.window.after(50,self.update)
        self.window.mainloop()

    def __onclose(self):
        self.window.destroy()
        for thread in self.threads:
            thread.exit()
 
stepLock = Lock()
stepCondition = Condition(stepLock)
controller = Controller(stepLock,stepCondition)

class _StopAndPlay:
    def __init__(self):
        self.lock = Lock()
        self.condition = Condition(self.lock)
        self.stepLock = stepLock
        self.stepCondition = stepCondition
        self.running=True
        self.controller = controller
    
    def stop(self):
        with self.lock:
            self.running=False
    
    def play(self):
        with self.lock:
            self.running = True
            self.condition.notifyAll()
    
    def run(self):
        if self.controller.isStopped:
            with self.stepLock:
                while self.controller.step<=0 and self.controller.isStopped:
                    self.stepCondition.wait()
                self.controller.decreaseStep()
class GraphLock:
    __id = 1
    def __init__(self):
        self.id = GraphLock.__id
        GraphLock.__id+=1
        self.controller=controller
        self.controller.addLock(self)
        self.waitLock = Lock()
        self.lock = Lock()
        self.canAcquire=False
        self.isReleased = False
        self.isInWait = False
        self.releaseLock=Lock()
        self.releaseCondition = Condition(self.releaseLock)        
        self.waitCondition = Condition(self.waitLock)
        self.lockCondition=Lock()
        self.condCondition=Condition(self.lockCondition)
        self.condionThread={}
        self.playController = _StopAndPlay()

    def setName(self,name):
        self.controller.setLockName(self,name)
    def acquire(self):
        self.waitLock.acquire()
        self.isReleased=False
        self.playController.run()
        sleepTime = self.controller.setWaitThread(current_thread(),self)
        sleep(sleepTime)
        self.waitLock.release()
        self.lock.acquire()
        self.playController.run()
        self.controller.drawFutureLockThread(current_thread(),self)
        sleep(2)
        self.controller.setAcquireThread(current_thread(),self)
        sleep(3)
    
    def release(self):
        self.releaseLock.acquire()
        if current_thread() in self.condionThread.keys():
            self.controller.setAcquireThreadFromCondition(current_thread(),self,self.condionThread[current_thread()])
            del self.condionThread[current_thread()]
            sleep(3)
        self.playController.run()
        self.controller.setReleaseThread(current_thread(),self)
        while not self.isReleased :
            self.releaseCondition.wait()
        self.releaseLock.release()
        self.isReleased = False
        self.lock.release()
        sleep(2)
    
    def addConditionThread(self,thread,condition):
        self.playController.run()
        self.controller.setThreadInCondition(thread,self,condition)
        self.condionThread[thread]=condition

    def getId(self):
        return self.id


class GraphThread(Thread):
    def __init__(self):
        super().__init__()
        self.controller=controller
        self.controller.addThread(self)
    
    def exit(self):
        os._exit(0)        
        

class GraphCondition(threading.Condition):
    def __init__(self,glock):
        super().__init__(glock.lock)
        self.glock = glock
        self.controller=controller
        self.name=str(self.glock.getId())
        self.controller.addCondition(self,self.glock)
        
    
    def wait(self):
        self.glock.addConditionThread(current_thread(),self)
        super().wait()

    def notify(self, waiters=1):
        self.controller.notifyLock(self.glock,self,False)
        super().notify(waiters)


    def notifyAll(self):
        self.controller.notifyLock(self.glock,self,True)
        super().notify(len(self._waiters))
    
    
    def setName(self,name):
        self.controller.setConditionName(self,self.glock,name)

def startGraph():
    controller.start()
    

