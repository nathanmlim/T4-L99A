import os,glob,re
import numpy as np
import matplotlib.pyplot as plt
from optparse import OptionParser
from collections import Counter

parser = OptionParser()

parser.add_option("-d","--directory", dest="dir")
parser.add_option("-f","--filename", dest="fname")
parser.add_option("-t","--header", dest="header")
parser.add_option("-r","--replica", dest="repnum")
parser.add_option("-e","--energy",action="store_true",dest="plotene",default=False)
(options,args) = parser.parse_args()

def loadrmsd(file):
    
    #Start at frame5 to frame 187 to mach sliding time
    #Frames output every 24ps, sliding time is averaged every 30ps...
    #s_start = int(1)
    #s_end = int(210) #5ns
    #s_end = int(-22) #25ns
    
    #Load rmsd file for each replica
    rmsddata = np.genfromtxt(file, skip_header=1, dtype=float)
    states = np.argmin(rmsddata[:,1:],axis=1)

    return rmsddata, states

def loadene(file):
   #Load ene file for each replica
   enedata = np.genfromtxt(file, skip_header=9, dtype=float)
   return enedata

def freqcount(state):
   freq = Counter(state)
   c_freq = freq[0] / float( len(state) )
   i_freq = freq[1] / float( len(state) )
   o_freq = freq[2] / float( len(state) )

   return c_freq,i_freq,o_freq
             
def rmsdplot(rmsddata,enedata,repnum,plotene=False):
   #Unpack rmsd dictionary
   data = rmsddata[0]
   state =rmsddata[1]

   print "{} - Plotting RMSD of replica{}".format(options.dir, repnum)

   #Change frame numbers to timepoints
   #Frames output every ~24ps
   time = data[:,0] * 24
   
   #Count frequency of states for scatterplot
   c_freq, i_freq, o_freq = freqcount(state)
  
   #Lineplot of RMSD relative to Closed state
   fig, ax = plt.subplots(1, sharex=True, figsize=(10,5))
   ax.plot( time, data[:,1], 'k', linewidth=2)

   if plotene == True:
      print "{} - Overlaying energies on replica{}".format(options.dir, repnum)
      #Unpack energy dictionary
      #Skipping time 0
      enetime = enedata[:,0]
      enetotal = enedata[:,1]
      ax1 = ax.twinx()
      ax1.plot( enetime, enetotal, '-r', linewidth=5)
   
   o=None
   #Colored Scatterplot points to state of minimum RMSD
   for t,s,r in zip(time,state,data[:,1]):
      if s == 0:
         c = ax.scatter( t, r, color = 'purple', clip_on=False, s=75)
      elif s == 1:
         i = ax.scatter( t, r, color = 'c', clip_on=False, s=75)
      elif s == 2:
         o = ax.scatter( t, r, color = 'g', clip_on=False, s=75)

   #Legend settings
   box = []
   if o:
      lgd = ax.legend( (c, i, o), ('C {:.2%}'.format(c_freq) , 'I {:.2%}'.format(i_freq), 'O {:.2%}'.format(o_freq) ) , scatterpoints=1, loc=4, bbox_to_anchor=(0.,1.02,1.,1.), ncol=3, prop={'size':8})
   if not o:
      lgd = ax.legend( (c, i), ('C {:.2%}'.format(c_freq) , 'I {:.2%}'.format(i_freq) ) , scatterpoints=1, loc=4, bbox_to_anchor=(0.,1.02,1.,1.), ncol=2, prop={'size':8})
   box.append(lgd)
   
   #Axis settings
   plt.xlabel("Time(ps)")
   plt.xlim( (0,5000) )
   major_xticks = np.arange(0,5000,500)
   minor_xticks = np.arange(0,5000,250)
   ax.set_xticks(major_xticks) 
   ax.set_xticks(minor_xticks,minor=True)
   ax.xaxis.grid(True)
   
   #Title and Output settings
   ax.set_title(options.header + r' $\lambda_{%s}$' %repnum, x=0.25)
   fig.text(0.07, 0.5, 'RMSD to Closed', va='center', rotation='vertical')

   if not os.path.exists("{}/plots".format(options.dir)):
      os.makedirs("{}/plots".format(options.dir))

   if plotene == True:
      plt.savefig("{}/plots/RMSDene-{}{}.png".format(options.dir,options.fname,repnum), additional_artists=box) #bbox_inches='tight')
   else:
      plt.savefig("{}/plots/RMSD-{}{}.png".format(options.dir,options.fname,repnum), additional_artists=box) #bbox_inches='tight')

   
def compare_rmsdplot(lam0,lam1):
   print "{} - Plotting RMSD of end states".format(options.dir)
   #Unpack the dictionary
   data0 = lam0[0]
   state0 = lam0[1]
   data1 = lam1[0]
   state1 = lam1[1]

   #Change frame numbers to timepoints
   #Frames output every ~24ps
   time = data0[:,0] * 24
  
   fig, ax = plt.subplots(2, sharex=True, sharey=True, figsize=(10,5) )
   box = []
   
   c_freq, i_freq, o_freq = freqcount(state0)
   o=None
   ax[0].plot( time, data0[:,1,], 'k', linewidth=2)
   #Colored Scatterplot points to state of minimum RMSD
   for t,s,r in zip(time,state0,data0[:,1]):
      if s == 0:
         c = ax[0].scatter( t, r, color = 'purple', clip_on=False, s=75)
      elif s == 1:
         i = ax[0].scatter( t, r, color = 'c', clip_on=False, s=75)
      elif s == 2:
         o = ax[0].scatter( t, r, color = 'g', clip_on=False, s=75)

   #Legend settings
   if o:
      lgd = ax[0].legend( (c, i, o), ('C {:.2%}'.format(c_freq) , 'I {:.2%}'.format(i_freq), 'O {:.2%}'.format(o_freq) ) , scatterpoints=1, loc=4, bbox_to_anchor=(0.,1.02,1.,1.), ncol=3, prop={'size':8})
   if not o:
      lgd = ax[0].legend( (c, i), ('C {:.2%}'.format(c_freq) , 'I {:.2%}'.format(i_freq) ) , scatterpoints=1, loc=4, bbox_to_anchor=(0.,1.02,1.,1.), ncol=2, prop={'size':8})
   box.append(lgd)
    
   c_freq, i_freq, o_freq = freqcount(state1)
   o1=None
   ax[1].plot( time, data1[:,1], 'k', linewidth=2)
   #Colored Scatterplot points to state of minimum RMSD
   for t,s,r in zip(time,state1,data1[:,1]):
      if s == 0:
         c1 = ax[1].scatter( t, r, color = 'purple', clip_on=False, s=75)
      elif s == 1:
         i1 = ax[1].scatter( t, r, color = 'c', clip_on=False, s=75)
      elif s == 2:
         o1 = ax[1].scatter( t, r, color = 'g', clip_on=False, s=75)

   if o1:
      lgd1 = ax[1].legend( (c, i, o), ('C {:.2%}'.format(c_freq) , 'I {:.2%}'.format(i_freq), 'O {:.2%}'.format(o_freq) ) , scatterpoints=1, loc=4, bbox_to_anchor=(0.,1.02,1.,1.), ncol=3, prop={'size':8})
   if not o1:
      lgd1 = ax[1].legend( (c, i), ('C {:.2%}'.format(c_freq) , 'I {:.2%}'.format(i_freq) ) , scatterpoints=1, loc=4, bbox_to_anchor=(0.,1.02,1.,1.), ncol=2, prop={'size':8})
   box.append(lgd1)

   #Axis settings
   plt.xlabel("Time(ps)")
   plt.xlim( (0,5000) )
   major_xticks = np.arange(0,5000,500)
   minor_xticks = np.arange(0,5000,250)
   ax[0].set_xticks(major_xticks)
   ax[0].set_xticks(minor_xticks,minor=True)
   ax[0].xaxis.grid(True)
   ax[1].set_xticks(major_xticks)
   ax[1].set_xticks(minor_xticks,minor=True)
   ax[1].xaxis.grid(True)
   
   #Title and Output settings
   ax[0].set_title(options.header + r' $\lambda_0$', x=0.25)
   ax[1].set_title(options.header + r' $\lambda_{11}$', x=0.25)
   fig.text(0.07, 0.5, 'RMSD to Closed', va='center', rotation='vertical')
   plt.savefig("{}/RMSD-0v1.png".format(options.dir,options.fname), additional_artists=box) #, bbox_inches='tight')



rmsdfiles = sorted(glob.glob("{}/{}*.rmsd".format(options.dir, options.fname)))
enefiles = sorted(glob.glob("{}/{}*.ene".format(options.dir, options.fname)))

#Load ene files
allene = {}
for file in enefiles:
    repnum = file.strip('.ene').split('replica')[1]
    allene[repnum] = loadene(file)

#Load RMSD files
allrmsd = {}
for file in rmsdfiles:
   repnum = file.strip('.rmsd').split('replica')[1]
   rmsddata, states = loadrmsd(file)
   allrmsd[repnum] = [rmsddata, states]


#Plot RMSD for replicas
try:
   if int(options.repnum) <= 11:   
      rmsdplot(allrmsd[options.repnum],allene[options.repnum],options.repnum, options.plotene)
except ValueError:
   if options.repnum == 'all':
      for i in range(12):
         rmsdplot(allrmsd[str(i)],allene[str(i)],i,options.plotene)

#Plot RMSD for end states only
compare_rmsdplot(allrmsd['0'],allrmsd['11'])
