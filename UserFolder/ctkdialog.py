"""fork of dialog.py but for customtkinter"""
# pip install customtkinter
from customtkinter import CTkToplevel, CTkEntry, CTkCheckBox, CTkSlider, CTkOptionMenu, CTkLabel, CTkFrame, CTkButton

import tkinter
import warnings
from enum import EnumMeta

from . import Config, getConfig
from .dialog import ConfigDialogEvent

__all__ = ['CTkConfigDialog']

class CTkConfigDialog(CTkToplevel):
    def __init__(self, config:Config=None, parent=None):
        if config is None: config = getConfig()
        if isinstance(config, Config)==False: raise TypeError('config argument should be UserFolder.Config')
        super().__init__(parent)
        super().title('Configure')
        super().resizable(True, False)
        super().minsize(400, 0)
        super().attributes('-topmost', True)
        self.config(padx=20, pady=10)
        self._config = config
        self.options = {}
        self.datatypes = []
        self.variables = {}

        self.add_datatype(str, lambda e: self.__builtin_datatype('str', e))
        self.add_datatype(bool, lambda e: self.__builtin_datatype('bool', e))
        self.add_datatype(int, lambda e: self.__builtin_datatype('int', e))
        self.add_datatype(float, lambda e: self.__builtin_datatype('float', e))
        self.add_datatype(range, lambda e: self.__builtin_datatype('range', e))
        self.add_datatype(EnumMeta, lambda e: self.__builtin_datatype('enum', e))

        self.row = 0
        self.column = 0
        for o in config.registry: self.create_option(key=o, **config.registry[o])
        self.footer()

        self.grid_columnconfigure(0, weight=1)

    def __builtin_datatype(self, type, e:ConfigDialogEvent):
        var = None
        from_ = 0
        to = 1
        if e.from_ is not None: from_ = e.from_
        if e.to is not None: to = e.to
        match type:
            case'str':
                var = tkinter.StringVar()
                var.set(str(e.default))
                CTkEntry(self, textvariable=var).grid(row=e.row, column=e.column, sticky=tkinter.EW)
            
            case 'bool':
                var = tkinter.BooleanVar()
                var.set(bool(e.default))
                CTkCheckBox(self, variable=var, text='', onvalue=True, offvalue=False).grid(row=e.row, column=e.column, sticky=tkinter.W)
                
            case 'int':
                var = tkinter.IntVar()
                var.set(int(e.default))
                CTkEntry(self, textvariable=var).grid(row=e.row, column=e.column, sticky=tkinter.EW)
                
            case 'float':
                var = tkinter.DoubleVar()
                var.set(float(e.default))
                CTkEntry(self, textvariable=var).grid(row=e.row, column=e.column, sticky=tkinter.EW)
                
            case 'range':
                var = tkinter.IntVar()
                var.set(int(e.default))
                CTkSlider(self, variable=var, from_=from_, to=to).grid(row=e.row, column=e.column, sticky=tkinter.EW)

            case 'enum':
                var = tkinter.StringVar()
                var.set(str(e.default))

                values = []
                for v in e.values:
                    values.append(str(v))

                CTkOptionMenu(self, variable=var, values=values).grid(row=e.row, column=e.column, sticky=tkinter.EW)
            
            case _:
                warnings.warn('Unknown builtin datatype')
                return self.__builtin_datatype('str', e)
        return var
    
    def add_datatype(self, cls, factory):
        self.datatypes.append({'class': cls, 'factory': factory})

    def create_option(self, key, datatype=None, title:str=None, description:str=None, from_:float=None, to:float=None):
        """Add a new option to the screen"""
        # create label
        label = str(key).title()
        if title!=None: label = title

        for type in self.datatypes:
            if datatype == type['class'] or datatype.__class__ == type['class']:
                CTkLabel(self, text=label, anchor=tkinter.W).grid(row=self.row, column=self.column, sticky=tkinter.EW)
                CTkLabel(self, text=description, padx=10).grid(row=self.row+1, column=self.column+1, sticky=tkinter.W)
                values = []
                if datatype.__class__ == EnumMeta:
                    values = list(datatype)

                default = self._config.getItem(key)
                var = type['factory'](ConfigDialogEvent(self, default, self.row+1, self.column, from_, to, values))
                self.variables[str(key)] = var
                self.row += 2

    def save(self):
        for k in self.variables:
            var = self.variables.get(k)
            self._config.setItem(str(k), var.get())
        self.destroy()

    def footer(self):
        """Add the footer to the bottom of the screen"""
        foot = CTkFrame(self)
        CTkButton(foot, text='Cancel', command=self.destroy).grid(row=0, column=0, padx=5, sticky=tkinter.E)
        CTkButton(foot, text='Save', command=self.save).grid(row=0, column=1, padx=5, sticky=tkinter.E)

        foot.grid_columnconfigure(0, weight=1)
        foot.grid(row=self.row, columnspan=2, column=0, sticky=tkinter.EW, pady=(10, 0))
