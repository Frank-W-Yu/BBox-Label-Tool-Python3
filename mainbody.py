#-------------------------------------------------------------------------------
# Name:        Object bounding box label tool for Python 3 64 bit
# Purpose:     Label object bboxes for ImageNet Detection data
# Author:      Weijie Yu
# Created:     06/08/2018

#
#------------------------------------------------------------------------------

import Tkinter as tk
from PIL import Image, ImageTk
import os
import glob
import random

COLORS = ['red', 'blue', 'yellow', 'pink', 'cyan', 'green', 'black']
SIZE = 256, 256

class LabelTool(object):
    def __init__(self, root):
        self.parent = root
        self.parent.title("BBox Label Tool")
        self.frame = tk.Frame(self.parent)
        self.frame.pack(fill=tk.BOTH, expand=1)
        self.parent.resizable(width=tk.FALSE, height=tk.FALSE)

        # initialize global state
        self.imageDir = ''
        self.imageList = []
        self.egDir = ''
        self.egList = []
        self.outDir = ''
        self.cur = 0
        self.total = 0
        self.category = 0
        self.imagename = ''
        self.labelfilename = ''
        self.tkimg = None

        # initialize mouse state
        self.STATE = {}
        self.STATE['click'] = 0
        self.STATE['x'], self.STATE['y'] = 0, 0

        # reference to bbox
        self.bboxIdList = []
        self.bboxId = None
        self.bboxList = []
        self.hl = None
        self.vl = None

        # ----------------- GUI stuff ---------------------
        # dir entry & load
        self.label = tk.Label(self.frame, text="Image Dir:")
        self.label.grid(row=0, column=0, sticky=tk.E)
        self.entry = tk.Entry(self.frame)
        self.entry.grid(row=0, column=1, sticky=tk.W + tk.E)
        self.ldBtn = tk.Button(self.frame, text="Load", command=self.loadDir)
        self.ldBtn.grid(row=0, column=2, sticky=tk.W + tk.E)

        # main panel for labeling
        self.mainPanel = tk.Canvas(self.frame, cursor='tcross')
        self.mainPanel.bind("<Button-1>", self.mouseClick)
        self.mainPanel.bind("<Motion>", self.mouseMove)
        self.parent.bind("<Escape>", self.cancelBBox)  # press <Espace> to cancel current bbox
        self.parent.bind("s", self.cancelBBox)
        self.parent.bind("a", self.prevImage)  # press 'a' to go backforward
        self.parent.bind("d", self.nextImage)  # press 'd' to go forward
        self.mainPanel.grid(row=1, column=1, rowspan=4, sticky=tk.W + tk.N)

        # showing bbox info & delete bbox
        self.lb1 = tk.Label(self.frame, text='Bounding boxes:')
        self.lb1.grid(row=1, column=2, sticky=tk.W + tk.N)
        self.listbox = tk.Listbox(self.frame, width=22, height=12)
        self.listbox.grid(row=2, column=2, sticky=tk.N)
        self.btnDel = tk.Button(self.frame, text='Delete', command=self.delBBox)
        self.btnDel.grid(row=3, column=2, sticky=tk.W + tk.E + tk.N)
        self.btnClear = tk.Button(self.frame, text='ClearAll', command=self.clearBBox)
        self.btnClear.grid(row=4, column=2, sticky=tk.W + tk.E + tk.N)

        # control panel for image navigation
        self.ctrPanel = tk.Frame(self.frame)
        self.ctrPanel.grid(row=5, column=1, columnspan=2, sticky=tk.W + tk.E)
        self.prevBtn = tk.Button(self.ctrPanel, text='<< Prev', width=10, command=self.prevImage)
        self.prevBtn.pack(side=tk.LEFT, padx=5, pady=3)
        self.nextBtn = tk.Button(self.ctrPanel, text='Next >>', width=10, command=self.nextImage)
        self.nextBtn.pack(side=tk.LEFT, padx=5, pady=3)
        self.progLabel = tk.Label(self.ctrPanel, text="Progress:     /    ")
        self.progLabel.pack(side=tk.LEFT, padx=5)
        self.tmpLabel = tk.Label(self.ctrPanel, text="Go to Image No.")
        self.tmpLabel.pack(side=tk.LEFT, padx=5)
        self.idxEntry = tk.Entry(self.ctrPanel, width=5)
        self.idxEntry.pack(side=tk.LEFT)
        self.goBtn = tk.Button(self.ctrPanel, text='Go', command=self.gotoImage)
        self.goBtn.pack(side=tk.LEFT)

        # example pannel for illustration
        self.egPanel = tk.Frame(self.frame, border=10)
        self.egPanel.grid(row=1, column=0, rowspan=5, sticky=tk.N)
        self.tmpLabel2 = tk.Label(self.egPanel, text="Examples:")
        self.tmpLabel2.pack(side=tk.TOP, pady=5)
        self.egLabels = []
        for i in range(3):
            self.egLabels.append(tk.Label(self.egPanel))
            self.egLabels[-1].pack(side=tk.TOP)

        # display mouse position
        self.disp = tk.Label(self.ctrPanel, text='')
        self.disp.pack(side=tk.RIGHT)

        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(4, weight=1)


