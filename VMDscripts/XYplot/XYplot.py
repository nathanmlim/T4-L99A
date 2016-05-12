import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
from scipy.stats import norm
import stats
import numpy as np
plt.rcParams['legend.markerscale'] = 0
#plt.rcParams['legend.handletextpad'] = 0
plt.rcParams['legend.handlelength'] = 0


def xyplot(data,xlabel,units):
      if units == 'kcal':
         bounds = 1
      else:
         bounds = 4
      ideal_line = [i for i in range(-7,7)]
      line1 = [i+bounds for i in ideal_line]
      line2 = [i-bounds for i in ideal_line]
      #Plot data      
      ax1 = plt.figure(figsize=[10,10]).add_subplot(111)
      """
      #C vs O
      x = data[:,0]
      xerr = data[:,1]
      y = data[:,2]
      yerr = data[:,3]
      RMSE = stats.rmse(x, y)
      R = stats.rsquared(x, y)
      N = len(y)

      #ax1.axis([0,4,0,4])
      ax1.axis([-2,3,-2,3])
      ax1.errorbar(x,y, xerr=[xerr,xerr], yerr=[yerr,yerr], fmt='o', color='black', markersize=10)
      ax1.plot(ideal_line,ideal_line, color='red')
      ax1.plot(ideal_line,line1, linestyle='--', color='red')
      ax1.plot(ideal_line,line2, linestyle='--', color='red')
      ax1.set_xlabel(r'$\Delta\Delta$G Closed ({}/mol)'.format(units), fontsize=20)
      ax1.set_ylabel(r'$\Delta\Delta$G Open ({}/mol)'.format(units), fontsize=20)
      txt = "RMSI={:.2}".format(RMSE)#+r"$R^2$={:.2}".format(R)
      """
      ###C/O vs Ex
      exp = data[:,0]
      experr = data [:,1]
      c = data[:,2]
      cerr = data[:,3]
      o = data[:,4]
      oerr = data[:,5]

      ax1.axis([-2.5,1.5,-2.5,1.5])
      ax1.errorbar(exp, c,xerr=[experr,experr], yerr=[cerr,cerr], fmt='o' , color='purple',markersize=10)
      ax1.errorbar(exp, o,xerr=[experr,experr], yerr=[oerr,oerr], fmt='o', color='g', markersize=10)
      cRMSE = stats.rmse(c, exp)
      oRMSE = stats.rmse(o, exp)
      cR = stats.rsquared(c, exp)
      oR = stats.rsquared(o,exp)
      cN = len(c)
      oN = len(o)
      ax1.plot(ideal_line,ideal_line, color='black')
      ax1.plot(ideal_line,line1, linestyle='--', color='black')
      ax1.plot(ideal_line,line2, linestyle='--', color='black')
      ax1.set_xlabel(r' $\Delta\Delta$G exp  ({}/mol)'.format(units), fontsize=20)
      ax1.set_ylabel(r' $\Delta\Delta$G calc ({}/mol)'.format(units), fontsize=20)
      txt = r"$RMSE^C$"+"= {:.2}\n".format(cRMSE)+r"$RMSE^O$"+"= {:.2}".format(oRMSE)#+r"$R^2:$ C={:.2} O={:.2}".format(cR,oR)
      

      #Set axes parameters
      ax1.tick_params(axis='both',labelsize=18)


      #Figure caption
      #an = ax1.annotate(txt, xy=(0.5,-1), ha='center', xytext=(0,-60), xycoords='axes fraction', textcoords='offset points', bbox=dict(boxstyle="square",fc="w"))
      #wrapText(an)
      leg = ax1.legend([txt],loc=2, handlelength=0,handletextpad=0,fancybox=True,fontsize=20)
      #for item in leg.legendHandles:
      #   item.set_visible(False)
      plt.savefig('./exp_pREST_xyplot.png', bbox_inches='tight')
      plt.cla()

# Text Wrapping
# Defines wrapText which will attach an event to a given mpl.text object,
# wrapping it within the parent axes object.  Also defines a the convenience
# function textBox() which effectively converts an axes to a text box.
def wrapText(text, margin=4):
    """ Attaches an on-draw event to a given mpl.text object which will
        automatically wrap its string wthin the parent axes object.

        The margin argument controls the gap between the text and axes frame
        in points.
    """
    ax = text.get_axes()
    margin = margin / 72 * ax.figure.get_dpi()

    def _wrap(event):
        """Wraps text within its parent axes."""
        def _width(s):
            """Gets the length of a string in pixels."""
            text.set_text(s)
            return text.get_window_extent().width

        # Find available space
        clip = ax.get_window_extent()
        x0, y0 = text.get_transform().transform(text.get_position())
        if text.get_horizontalalignment() == 'left':
            width = clip.x1 - x0 - margin
        elif text.get_horizontalalignment() == 'right':
            width = x0 - clip.x0 - margin
        else:
            width = (min(clip.x1 - x0, x0 - clip.x0) - margin) * 2

        # Wrap the text string
        words = [''] + _splitText(text.get_text())[::-1]
        wrapped = []

        line = words.pop()
        while words:
            line = line if line else words.pop()
            lastLine = line

            while _width(line) <= width:
                if words:
                    lastLine = line
                    line += words.pop()
                    # Add in any whitespace since it will not affect redraw width
                    while words and (words[-1].strip() == ''):
                        line += words.pop()
                else:
                    lastLine = line
                    break

            wrapped.append(lastLine)
            line = line[len(lastLine):]
            if not words and line:
                wrapped.append(line)

        text.set_text('\n'.join(wrapped))

        # Draw wrapped string after disabling events to prevent recursion
        handles = ax.figure.canvas.callbacks.callbacks[event.name]
        ax.figure.canvas.callbacks.callbacks[event.name] = {}
        ax.figure.canvas.draw()
        ax.figure.canvas.callbacks.callbacks[event.name] = handles

    ax.figure.canvas.mpl_connect('draw_event', _wrap)

def _splitText(text):
    """ Splits a string into its underlying chucks for wordwrapping.  This
        mostly relies on the textwrap library but has some additional logic to
        avoid splitting latex/mathtext segments.
    """
    import textwrap
    import re
    math_re = re.compile(r'(?<!\\)\$')
    textWrapper = textwrap.TextWrapper()

    if len(math_re.findall(text)) <= 1:
        return textWrapper._split(text)
    else:
        chunks = []
        for n, segment in enumerate(math_re.split(text)):
            if segment and (n % 2):
                # Mathtext
                chunks.append('${}$'.format(segment))
            else:
                chunks += textWrapper._split(segment)
        return chunks

def textBox(text, axes, ha='left', fontsize=12, margin=None, frame=True, **kwargs):
    """ Converts an axes to a text box by removing its ticks and creating a
        wrapped annotation.
    """
    if margin is None:
        margin = 6 if frame else 0
    axes.set_xticks([])
    axes.set_yticks([])
    axes.set_frame_on(frame)

    an = axes.annotate(text, fontsize=fontsize, xy=({'left':0, 'right':1, 'center':0.5}[ha], 1), ha=ha, va='top',
                       xytext=(margin, -margin), xycoords='axes fraction', textcoords='offset points', **kwargs)
    wrapText(an, margin=margin)
    return an


data = np.genfromtxt('expdata_pREST.txt')
xyplot(data,'ddGexp','kcal')
