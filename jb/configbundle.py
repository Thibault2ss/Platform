# -*- coding: utf-8 -*-
import os
from os.path import isfile, join, getmtime, isdir
import ast
from datetime import datetime

class ConfigBundle:

    def __init__(self, configb_path):
        self.init_line=""
        self.filepath=configb_path
        self.presets={}
        self.settings={}
        self.filament_list=[]
        self.print_list=[]
        self.printer_list=[]
        self.config_list=[]
        self.parse(configb_path)



    def parse(self, configb_path):

        with open(configb_path,'r') as file:
            print "4000"
            for l in file:
                # remove all spaces and endlines
                line = self.r(l)

                if line.startswith("#"):
                    self.init_line = l

                elif line.startswith("[filament:"):
                    name=line[1:-1].split(':',1)[1]
                    self.filament_list.append(name)

                elif line.startswith("[print:"):
                    name=line[1:-1].split(':',1)[1]
                    self.print_list.append(name)

                elif line.startswith("[printer:"):
                    name=line[1:-1].split(':',1)[1]
                    self.printer_list.append(name)

        with open(configb_path,'r') as file:
            print "4001"
            preset_section = 0
            settings_section = 0
            for l in file:
                # remove all spaces and endlines
                line = self.r(l)

                if (preset_section or settings_section) and (l.startswith(" ") or l.startswith("\n") or l.startswith("\r") or l.startswith("[")) : #end of section
                    preset_section = 0
                    settings_section = 0

                if preset_section:
                    name = line.split("=",1)[0]
                    value = line.split("=",1)[1]
                    self.presets[name] = value
                elif settings_section:
                    name = line.split("=",1)[0]
                    value = line.split("=",1)[1]
                    self.settings[name] = value

                if line.startswith("[presets]"):
                    preset_section = 1
                elif line.startswith("[settings]"):
                    settings_section = 1
            print "4002"

    def unbundle_in(self, destination_dir, template_path):

        dico = {"filament" : self.filament_list , "printer" : self.printer_list , "print" : self.print_list }

        for param , paramlist in dico.iteritems():
            for element in paramlist:
                new_file = join( destination_dir, param, "%s.ini"%element)
                with open(new_file,'wb+') as destination:
                    destination.write(self.init_line + "\n")
                    with open(self.filepath, 'r') as f:
                        sectionstart = 0
                        for line in f:
                            if sectionstart and (line.startswith(" ") or line.startswith("\n") or line.startswith("\r") or line.startswith("[")):
                                sectionstart = 0
                                break
                            if sectionstart:
                                destination.write(line)
                            if line.startswith("[%s:%s"%(param, element)):
                                sectionstart = 1


        # create slic3r.ini
        new_file = join( destination_dir, "slic3r.ini")
        with open(new_file, 'wb+') as destination:
            # write the beginning from template
            with open(template_path, 'r') as f :
                for line in f:
                    destination.write(line)

            # write the preset from configbundle

            with open(self.filepath, 'r') as f:
                preset_section = 0
                recent_section = 0
                for line in f:
                    if (preset_section or recent_section) and (line.startswith(" ") or line.startswith("\n") or line.startswith("\r") or line.startswith("[")):
                        preset_section = 0
                        recent_section = 0
                    if preset_section:
                        destination.write(line)
                    if recent_section:
                        destination.write(line)
                    if line.startswith("[presets]"):
                        preset_section = 1
                        destination.write("[presets]\n")
                    if line.startswith("[recent]"):
                        recent_section = 1
                        destination.write("[recent]\n")


    def append_to_section(self, section, param_name, value):


        with open(self.filepath, 'r') as f:
            index_section = 0
            index_param = 0

            for num, line in enumerate(f, 1):
                if index_section and (index_param or line.startswith("[")):
                    break
                if line.startswith("[%s"%section):
                    print 'found at line:', num
                    index_section = num
                if self.r(line.split("=",1)[0])==param_name:
                    print 'param already existing2:', param_name
                    index_param = num


        f1 = open(self.filepath, 'r')
        contents = f1.readlines()
        f1.close()

        if index_section:
            if index_param:
                # TODO: change this to replace param instead of doing nothing
                # contents.insert(index_param, "%s=%s\n"%(param_name,value))
                print "PARAM EXISTS ALREADY2"
            else:
                contents.insert(index_section + 1, "%s=%s\n"%(param_name,value))
            with open(self.filepath, 'w') as f:

                contents = "".join(contents)
                f.write(contents)
        else:

            with  open(self.filepath, 'a') as f:

                f.write("[%s]\n"%section)
                f.write("%s=%s\n"%(param_name,value))

    def readfirst(self, param):
        value = ""
        with open(self.filepath, 'r') as f:
            for line in f:
                param_name = self.r(line.split("=",1)[0])
                if param_name == param:
                    value = line.split("=",1)[1].replace("\n","").replace("\r","")
                    break
        return value

    def change_config_param(self, param, param_value, output_path):
        folder = os.path.dirname(self.filepath)
        with open(self.filepath, 'r') as f:
            with open(output_path, "wb+") as tf:
                for line in f:
                    param_name = self.r(line.split("=",1)[0])
                    if param_name == param:
                        tf.write("%s = %s\n"%(param, param_value))
                    else:
                        tf.write(line)
        return output_path




    def r(self, string):
        string = string.replace("\n","").replace("\r","").replace(" ","")
        return string
