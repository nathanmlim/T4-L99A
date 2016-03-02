import os,glob,re
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from optparse import OptionParser
from collections import Counter

parser = OptionParser()

parser.add_option("-d","--directory", dest="dir")
parser.add_option("-f","--filename", dest="fname")
parser.add_option("-t","--header", dest="header")
parser.add_option("-r","--replica", dest="repnum")
parser.add_option("-e","--energy",action="store_true",dest="plotene",default=False)
parser.add_option("-x","--timeframe",dest="timeframe")
(options,args) = parser.parse_args()

def loadrmsd(file,timeframe):
   #Load rmsd file for each replica
   rmsddata = np.genfromtxt(file, skip_header=1, dtype=float)
   states = np.argmin(rmsddata[:,1:],axis=1)

   sta,fin = timeframe.split('-')
   rmsddata = rmsddata[int(sta):int(fin),:]
   states = states[int(sta):int(fin)]

   return rmsddata, states

def loadene(file,timeframe):
   #Load ene file for each replica
   enedata = np.genfromtxt(file, skip_header=9, dtype=float)

   #Define timeframe for analysis
   sta,fin = timeframe.split('-')

   def find_nearest(array,value):
       idx = (np.abs(array-value)).argmin()
       return int(idx)

   #Convert framenum to timepoints and find nearest timepoint
   #Get its index for slicing
   sta = find_nearest(enedata[:,0], int(sta)*24)
   fin = find_nearest(enedata[:,0], int(fin)*24)

   enedata = enedata[sta:fin,:]

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
   time = data[:,0] * 24 *0.001
   
   #Count frequency of states for scatterplot
   c_freq, i_freq, o_freq = freqcount(state)
  
   #Lineplot of RMSD relative to Closed state
   fig, ax = plt.subplots(1, sharex=True, figsize=(10,5))
   ax.plot( time, data[:,1], 'k', linewidth=2)

   if plotene == True:
      print "{} - Overlaying energies on replica{}".format(options.dir, repnum)
      #Unpack energy dictionary
      #Skipping time 0
      enetime = enedata[:,0] *0.001
      enetotal = enedata[:,1]
      #Share x-axis
      ax1 = ax.twinx()
      ax1.set_ylim(-50000,0)
      ax1.plot( enetime, enetotal, '-r', linewidth=5)
   
   #Colored Scatterplot points to state of minimum RMSD
   for t,s,r in zip(time,state,data[:,1]):
      if s == 0:
         c = ax.scatter( t, r, color = 'purple', clip_on=False,s=75, label='C {:.2%}'.format(c_freq))
      elif s == 1:
         i = ax.scatter( t, r, color = 'c', clip_on=False, s=75, label='I {:.2%}'.format(i_freq))
      elif s == 2:
         o = ax.scatter( t, r, color = 'g', clip_on=False, s=75, label='O {:.2%}'.format(o_freq))
   
   #Legend Settings
   #Work around to eliminate duplicate items in legend
   handleobj = []
   handles,labels = ax.get_legend_handles_labels()
   uniqlabels = sorted(list(set(labels)))
   for uni in uniqlabels:
      idx = labels.index(uni)
      handleobj.append( handles[idx] )
   
   box = []
   lgd = ax.legend(handleobj, uniqlabels, scatterpoints=1, loc=4, bbox_to_anchor=(0.,1.02,1.,1.), ncol=3, prop={'size':8} )
   box.append(lgd)
   
   #X-Axis settings
   lowx = int(round(time[0]/0.5)*0.5)
   upx = int(round(time[-1]/0.5)*0.5)
   ax.set_xlabel("Time(ns)")
   plt.xlim( (lowx,upx) )
   major_xticks = np.arange(lowx,upx,1.0)
   minor_xticks = np.arange(lowx,upx,0.5)
   ax.set_xticks(major_xticks) 
   ax.set_xticks(minor_xticks,minor=True)
   ax.xaxis.grid(True)

   #Y-axis settings
   ax.set_ylim( (0.5,4.5) )
   major_yticks = np.arange(0.5,4.5,0.5)
   minor_yticks = np.arange(0.5,4.5,0.5)
   ax.set_yticks(major_yticks)
   ax.set_yticks(minor_yticks,minor=True)
   ax.yaxis.grid(True, which='major')

   
   #Title and Output settings
   ax.set_title(options.header + r' $\lambda_{%s}$' %repnum, x=0.25)
   fig.text(0.07, 0.5, 'RMSD to Closed', va='center', rotation='vertical')

   if not os.path.exists("{}/plots".format(options.dir)):
      os.makedirs("{}/plots".format(options.dir))

   if plotene == True:
      plt.savefig("{}/plots/eneRMSD-{}{}_{}-{}ns.png".format(options.dir,options.fname,repnum,lowx,upx), additional_artists=box) #bbox_inches='tight')
   else:
      plt.savefig("{}/plots/RMSD-{}{}_{}-{}ns.png".format(options.dir,options.fname,repnum,lowx,upx), additional_artists=box) #bbox_inches='tight')
   plt.close('all')
   
def compare_rmsdplot(lam0,lam1):
   print "{} - Plotting RMSD of end states".format(options.dir)
   #Unpack the dictionary
   data0 = lam0[0]
   state0 = lam0[1]
   data1 = lam1[0]
   state1 = lam1[1]

   #Change frame numbers to timepoints
   #Frames output every ~24ps
   time = data0[:,0] * 24 *0.001
  
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

   #Y-axis settings
   ax[0].set_ylim( (0.5,4.5) )
   ax[1].set_ylim( (0.5,4.5) )
   major_yticks = np.arange(0.5,4.5,.5)
   minor_yticks = np.arange(0.5,4.5,.5)
   ax[0].set_yticks(major_yticks)
   ax[0].set_yticks(minor_yticks,minor=True)
   ax[0].yaxis.grid(True, which='major')
   ax[1].set_yticks(major_yticks)
   ax[1].set_yticks(minor_yticks,minor=True)
   ax[1].yaxis.grid(True, which='major')

   #X-axis settings
   lowx = int(round(time[0]/0.5)*0.5)
   upx = int(round(time[-1]/0.5)*0.5)
   plt.xlabel("Time(ns)")
   plt.xlim( (lowx,upx) )
   major_xticks = np.arange(lowx,upx,1)
   minor_xticks = np.arange(lowx,upx,0.5)
   ax[0].set_xticks(major_xticks)
   ax[0].set_xticks(minor_xticks,minor=True)
   ax[0].xaxis.grid(True)
   ax[1].set_xticks(major_xticks)
   ax[1].set_xticks(minor_xticks,minor=True)
   ax[1].xaxis.grid(True)
   
   #Title and Output settings
   tline = options.header.strip().split()
   if 'pREST' in tline:
      subtitle = 'pREST'
   else:
      subtitle = ''
   ax[0].set_title(tline[0]+' '+subtitle+ r' $\lambda_0$', x=0.25)
   ax[1].set_title(tline[2]+' '+subtitle+ r' $\lambda_{11}$', x=0.25)
   fig.text(0.07, 0.5, 'RMSD to Closed', va='center', rotation='vertical')
   plt.savefig("{}/RMSD-0v1_{}-{}ns.png".format(options.dir,lowx,upx), additional_artists=box) #, bbox_inches='tight')
   plt.close('all')

def colormap(rmsddata,enedata):

   time = rmsddata['0'][0][:,0] * 24 *0.001
   lowx = int(round(time[0]/0.5)*0.5)
   upx = int(round(time[-1]/0.5)*0.5)

   n = len(rmsddata['0'][1])
   #Build numpy array of states for all replicas
   statelist = []
   for i in range(12):
       statelist.append( rmsddata[str(i)][1] )
   statearr = np.vstack(statelist)
   #Initialized our figure
   fig = plt.figure(figsize=(12,6))
   ax = fig.add_subplot(1,1,1)

   #Fix color map
   cmap = mpl.colors.ListedColormap(['purple','c','green'])
   #Set bounds, must be +-1 from max/min values
   bounds=[0,1,2,3]
   norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
   ax.imshow(statearr,cmap=cmap,norm=norm,interpolation='nearest',origin='lower',aspect='auto')

   plt.xticks(np.arange(-0.5,n,1))
   ax.xaxis.set_ticklabels([])
   ax.xaxis.grid(True, which='major',color='black',linewidth=1)

   #Y-axis parameters
   ax.set_yticks(np.arange(0,12,1.0))
   ax.set_yticks(np.arange(-0.5,12,1.0),minor=True)
   ax.yaxis.grid(True, which='minor',color='black', linestyle='-',linewidth=2)

   #plt.colorbar(img, cmap=cmap, norm=norm, boundaries=bounds, ticks=[0,1,2],orientation='horizontal')
   ax.set_title(options.header+' {}-{}ns Colormap'.format(lowx,upx), x=0.25)
   plt.savefig('{}/colormap_{}-{}ns.png'.format(options.dir,lowx,upx))
   plt.close('all')
      

rmsdfiles = sorted(glob.glob("{}/{}*.rmsd".format(options.dir, options.fname)))
enefiles = sorted(glob.glob("{}/{}*.ene".format(options.dir, options.fname)))


#Load ene files
allene = {}
for file in enefiles:
    repnum = file.strip('.ene').split('replica')[1]
    allene[repnum] = loadene(file,options.timeframe)

#Load RMSD files
allrmsd = {}
for file in rmsdfiles:
   repnum = file.strip('.rmsd').split('replica')[1]
   rmsddata, states = loadrmsd(file,options.timeframe)
   allrmsd[repnum] = [rmsddata, states]

#Plot RMSD for replicas
try:
   if int(options.repnum) <= 11:   
      rmsdplot(allrmsd[options.repnum],allene[options.repnum],options.repnum, options.plotene)     
      rmsdplot(allrmsd[options.repnum],allene[options.repnum],options.repnum, plotene=True)
except ValueError:
   if options.repnum == 'all':
      for i in range(12):
         rmsdplot(allrmsd[str(i)],allene[str(i)],i,options.plotene)
         rmsdplot(allrmsd[str(i)],allene[str(i)],i,plotene=True)

#Plot RMSD for end states only
compare_rmsdplot(allrmsd['0'],allrmsd['11'])
#Plot stackedbar graph for colormap of replicas
colormap(allrmsd,allene)
