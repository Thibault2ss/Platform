import os
import ast
from datetime import datetime

class TrackFile:

    def __init__(self, track_file):

        self.parse(track_file)



    def parse(self, git_file):
        with open(git_file,'r') as file:
            for line in file:
                if line.startswith("file cad"):
                    cad=ast.literal_eval(line.split('::',1)[1].replace('\n',''))
                    self.cad_list.append(cad)
                elif line.startswith("file amf"):
                    amf=ast.literal_eval(line.split('::',1)[1].replace('\n',''))
                    self.amf_list.append(amf)
                elif line.startswith("file config"):
                    config=ast.literal_eval(line.split('::',1)[1].replace('\n',''))
                    self.config_list.append(config)
                elif line.startswith("part"):
                    part=ast.literal_eval(line.split('::',1)[1].replace('\n',''))
                    self.part=part
                elif line.startswith("date exported"):
                    date=datetime.strptime(line.split('::',1)[1].replace('\n',''),'%d-%m-%Y %H:%M')
                    self.date_exported=date
                elif line.startswith("userid"):
                    self.userid=int(line.split('::',1)[1].replace('\n',''))
                elif line.startswith("username"):
                    self.username=line.split('::',1)[1].replace('\n','')
                elif line.startswith("file _3mf"):
                    _3mf=ast.literal_eval(line.split('::',1)[1].replace('\n',''))
                    self._3mf_list.append(_3mf)
