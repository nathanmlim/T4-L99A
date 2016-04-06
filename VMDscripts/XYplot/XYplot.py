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
      x = data[:,0]
      y = data[:,1]
      y1 = data[:,2]
      #y2 = data[:,2]
      if units == 'kcal':
         bounds = 1
      else:
         bounds = 4
      ideal_line = [i for i in range(-2,2)]
      line1 = [i+bounds for i in ideal_line]
      line2 = [i-bounds for i in ideal_line]
      #Plot data      
      ax1 = plt.figure(figsize=[10,10]).add_subplot(111)
      ax1.axis([-2,1,-2,1])
      ax1.scatter(x,y,color='purple', s=200, label='C')
      ax1.scatter(x,y1,color='g', s=200, label='O')
      ax1.plot(ideal_line,ideal_line, color='black')
      ax1.plot(ideal_line,line1, linestyle='--', color='black')
      ax1.plot(ideal_line,line2, linestyle='--', color='black')
      #Set axes parameters
      #ax1.set_xlim(-1*ymax,ymax)
      #ax1.set_ylim(-1*ymax,ymax)
      ax1.set_xlabel('{}({}/mol)'.format(xlabel,units))
      ax1.set_ylabel('ddG Predicted ({}/mol)'.format(units))
      #ax1.set_title(r'{} - {} ddG'.format( method, dGtype ))

      #Statistics
      #RMSE = stats.rmse(y, x)
      #R = stats.rsquared(y, x)
      #N = len(y)

      #Figure caption
      #txt = "Figure Subcaption Here\n"+"RMSE={:.2}".format(RMSE)+r" $R^2$={:.2}".format(R)+" N={}".format(N)
      #an = ax1.annotate(txt, xy=(0.5,-1), ha='center', xytext=(0,-60), xycoords='axes fraction', textcoords='offset points', bbox=dict(boxstyle="square",fc="w"))
      #wrapText(an)
      #ax1.legend([txt],loc=2,fontsize='small')
      plt.savefig('./results.png', bbox_inches='tight')
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


data = np.genfromtxt('expdata.txt')
xyplot(data,'ddGexp','kcal')
