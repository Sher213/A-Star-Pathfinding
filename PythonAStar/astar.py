import tkinter as tk
import random
import math
import threading

class NodePlacementError(Exception):
    pass

class Node:
    DIAGONAL_DIFF=14
    STRAIGHT_DIFF=10

    def __init__(self,canvas,x1,y1,x2,y2,row,col):
        #visual data
        self.rect=canvas.create_rectangle(x1,y1,x2,y2, fill="blue", tags="node")
        #positional data
        self.position = [row,col]
        #data related to algorithm
        self.f_cost=0
        self.g_cost=0
        self.h_cost=0
        self.parentNode = None
        self.traversable = True

    def setColour(self, colour, canvas):
        canvas.itemconfig(self.rect, fill=colour)

    def getPosition(self):
        return self.position

    def getGCost(self):
        return self.g_cost
    
    def getHCost(self):
        return self.h_cost

    def getFCost(self):
        return self.f_cost

    def getParent(self):
        return self.parentNode
    
    def isTraversable(self):
        return self.traversable

    def setTraversability(self, t):
        self.traversable = t

    def setParent(self, p):
        self.parentNode = p

    def setHCost(self, endNode):
        row_diff = abs(endNode.getPosition()[0]-self.getPosition()[0])
        col_diff = abs(endNode.getPosition()[1]-self.getPosition()[1])
        if row_diff <= col_diff:
            self.h_cost = self.DIAGONAL_DIFF*row_diff + self.STRAIGHT_DIFF*(col_diff-row_diff)
        else:
            self.h_cost = self.DIAGONAL_DIFF*col_diff + self.STRAIGHT_DIFF*(row_diff-col_diff)
    
    def setGCost(self):
        if not(self.parentNode.getPosition()[0] == self.getPosition()[0] or self.parentNode.getPosition()[1] == self.getPosition()[1]):
            self.g_cost+=self.DIAGONAL_DIFF
        else:
            self.g_cost+=self.STRAIGHT_DIFF

    def checkGCost(self, neighborNode):
        if not(neighborNode.getPosition()[0] == self.getPosition()[0] or neighborNode.getPosition()[1] == self.getPosition()[1]):
            return self.g_cost + self.DIAGONAL_DIFF
        else:
            return self.g_cost + self.STRAIGHT_DIFF

    def setFCost(self, endNode):
        self.setGCost()
        self.setHCost(endNode)
        self.f_cost = self.g_cost + self.h_cost
        
class UserConfigWindow(object):
    def __init__(self,master):
        top=self.top=tk.Toplevel(master)
        top.geometry("200x200")
        self.gridSize = 0
        self.startX = 0
        self.startY = 35
        self.endX = 0
        self.endY = 0
        self.l1=tk.Label(top,text="Choose Grid Size (NxN)")
        self.l1.place(x=40, y=0)
        self.e1=tk.Entry(top)
        self.e1.place(x=30, y=25)
        self.l2=tk.Label(top, text="Choose Start Node [X, Y]")
        self.l2.place(x=40, y=50)
        self.l2a=tk.Label(top, text="[")
        self.l2a.place(x=40, y=75)
        self.l2b=tk.Label(top, text=",")
        self.l2b.place(x=90, y=75)
        self.l2c=tk.Label(top, text="]")
        self.l2c.place(x=140, y=75)
        self.e2 = tk.Entry(top, width=5)
        self.e2.place(x=50, y=75)
        self.e3 = tk.Entry(top, width=5)
        self.e3.place(x=100, y=75)
        self.l3=tk.Label(top, text="Choose End Node [X, Y]")
        self.l3.place(x=40, y=100)
        self.l3a=tk.Label(top, text="[")
        self.l3a.place(x=40, y=125)
        self.l3b=tk.Label(top, text=",")
        self.l3b.place(x=90, y=125)
        self.l3c=tk.Label(top, text="]")
        self.l3c.place(x=140, y=125)
        self.e4 = tk.Entry(top, width=5)
        self.e4.place(x=50, y=125)
        self.e5 = tk.Entry(top, width=5)
        self.e5.place(x=100, y=125)
        self.b=tk.Button(top,text='Enter',command=self.setVals)
        self.b.place(x=75, y=150)
        self.errorMsg=tk.StringVar()
        self.l4 = tk.Label(top, textvariable=self.errorMsg)
        self.l4.place(x=0, y=175)

    def setVals(self):
        try:
            self.gridSize = int(self.e1.get())
            self.startX = int(self.e2.get()) - 1
            self.startY = int(self.e3.get()) - 1
            self.endX = int(self.e4.get()) - 1
            self.endY = int(self.e5.get()) - 1
            #make sure all values are less than the grid size
            if (self.startX > self.gridSize or self.startY > self.gridSize or self.endX > self.gridSize or self.endY > self.gridSize):
                raise NodePlacementError
            self.top.destroy()
        #error handling
        except NodePlacementError:
            self.errorMsg.set("Start and End Values <= GridSize!")
        except Exception:
            self.errorMsg.set("Invalid Entries. Integers Only!")

    def getVals(self):
        return [self.gridSize, self.startX, self.startY, self.endX, self.endY]
        

class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        
        userConfig = self.openUserConfigWindow()
        self.startX = userConfig[1]
        self.startY = userConfig[2]
        self.endX = userConfig[3]
        self.endY = userConfig[4]

        #set dimensions of window
        self.gridSize = userConfig[0]
        self.cellwidth = 25
        self.cellheight = 25
        self.width = self.gridSize*self.cellwidth
        self.height = (self.gridSize*self.cellheight) + 50
        self.canvas = tk.Canvas(self, width=self.width, height=self.height, borderwidth=0, highlightthickness=0)
        self.canvas.pack(side="top", fill="both", expand="true")

        #create grid of Nodes with user dimensions
        self.node = [[0 for x in range(self.gridSize)] for y in range(self.gridSize)]
        for column in range(self.gridSize):
            for row in range(self.gridSize):
                x1 = column*self.cellwidth
                y1 = row * self.cellheight
                x2 = x1 + self.cellwidth
                y2 = y1 + self.cellheight
                self.node[row][column] = Node(self.canvas,x1,y1,x2,y2,row,column)
        
        #highlight start and end points
        self.node[self.startY][self.startX].setColour('red', self.canvas)
        self.node[self.endY][self.endX].setColour('red', self.canvas)

        #create buttons to start algorithm or reset
        self.b1 = tk.Button(self, text='Start', command= lambda: self.aStar(self.node, self.node[self.startY][self.startX], self.node[self.endY][self.endX]))
        self.b1.place(x=10, y=self.height-40)
        self.b2 = tk.Button(self, text='Reset', command= self.reset)
        self.b2.place(x=50, y=self.height-40)
        self.canvas.tag_bind('node', '<Button-1>', self.setNodeTrav)

    def reset(self):
        self.destroy()
        self.__init__()

    #refresh the grid
    def refreshGrid(self):
        for column in range(self.gridSize):
            for row in range(self.gridSize):
                if (column == self.startX and row == self.startY) or (column == self.endX and row == self.startY):
                    self.node[row][column].setColour('red', self.canvas)
                if self.node[row][column].isTraversable() == True:
                    self.node[row][column].setColour('blue', self.canvas)
                if self.node[row][column].isTraversable() == False:
                    self.node[row][column].setColour('black', self.canvas)

    def openUserConfigWindow(self):
        #minimize main window on load
        self.iconify()
        #popup window to initialize user configuration
        config = UserConfigWindow(self.master)
        self.wait_window(config.top)
        self.deiconify()
        return config.getVals()

    def setNodeTrav(self, event):
        col = math.floor(event.x/self.cellwidth) 
        row = math.floor(event.y/self.cellheight)
        if not((col == self.startX and row == self.startY) or (col == self.endX and row == self.endY)):
            if self.node[row][col].isTraversable() == True:
                self.node[row][col].setTraversability(False)
                self.node[row][col].setColour('black', self.canvas)
            else:
                self.node[row][col].setTraversability(True)
                self.node[row][col].setColour('blue', self.canvas)

    def aStar(self, nodes, startNode, endNode):
        #refresh grid
        self.refreshGrid()

        open = [startNode]
        closed = []
        current = None

        while not(current == endNode):
            current = self.getLowestFCost(open)
            open.remove(current)
            closed.append(current)

            neighborLocs = self.getNodeNeighbors(current)
            for coord in neighborLocs:
                #neighbor g cost vs updated neighbor g cost
                oldPath = nodes[coord[0]][coord[1]].getGCost()
                newPath = nodes[coord[0]][coord[1]].checkGCost(current)
                if nodes[coord[0]][coord[1]].isTraversable() == False or nodes[coord[0]][coord[1]] in closed:
                    continue
                elif newPath < oldPath or not(nodes[coord[0]][coord[1]] in open):
                    nodes[coord[0]][coord[1]].setColour('green', self.canvas)
                    nodes[coord[0]][coord[1]].setParent(current)
                    nodes[coord[0]][coord[1]].setFCost(endNode)
                    if not(nodes[coord[0]][coord[1]] in open):
                        open.append(nodes[coord[0]][coord[1]])

        #visualize the path
        pathNode = current
        while not(pathNode is None):
            pathNode.setColour('red', self.canvas)
            pathNode = pathNode.getParent()

        return current

    def getNodeNeighbors(self, node):
        row=node.getPosition()[0]
        col=node.getPosition()[1]
        neighborsRough = [[row, col-1], [row-1, col-1], [row-1, col], [row-1, col+1], [row, col+1], [row+1, col+1], [row+1, col], [row+1, col-1]]
        neighborsNew = []
        for x in range(8):
            if (0 <= neighborsRough[x][0] < self.gridSize and  0 <= neighborsRough[x][1] < self.gridSize):
                neighborsNew.append(neighborsRough[x])
        return neighborsNew

    def getLowestFCost(self, nodes):
        def fCostofIndex(elem):
            return elem.getFCost()

        nodes.sort(key=fCostofIndex)
        return nodes[0]
        
    

if __name__ == "__main__":
    app = App()
    app.mainloop()
