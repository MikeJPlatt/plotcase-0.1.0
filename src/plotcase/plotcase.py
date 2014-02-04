
# pylint: disable-msg=E0611,F0401
from openmdao.main.interfaces import implements, ICaseRecorder, ICaseIterator
from pylab import plt
from matplotlib.widgets import CheckButtons


class PlotCaseIterator(list):
    """An iterator that returns :class:`Case` objects from a passed-in iterator
    of cases. This can be useful for runtime-generated cases from an
    optimizer, etc.
    """
    
    implements(ICaseIterator)
    
    def __init__(self, cases):
        super(PlotCaseIterator, self).__init__(cases)

    def get_attributes(self, io_only=True):
        """ We need a custom get_attributes because we aren't using Traits to
        manage our changeable settings. This is unfortunate and should be
        changed to something that automates this somehow."""
        
        attrs = {}
        attrs['type'] = type(self).__name__
        
        return attrs
class PlotCaseRecorder(object):
    """A CaseRecorder that plots convergence using matplotlib.
    
    The plot is automatically set up with separate curves for each parameter, plus one for the objective.  
    
    The legend in the plot also acts as a toggle switch: clicking on any parameter in the legend will enable/disable that data in the plot.
    """    
    
    implements(ICaseRecorder)
    
    def __init__(self, pause=0.05, logscale = False, title = 'PlotCaseRecorder Convergence Plot'): 
        
        self.pause = pause
        self.logscale = logscale
        self.title = title
        self.count = []
        self.initial = []
        
    def startup(self):
        """ Nothing needed for a plot case."""
        pass
    
    def getCount(self):
        self.initial.append(1)
        
    def get_parameters(self, case):
        
        parameters = case.keys(iotype = 'in', flatten = True)
        numParms = range(len(parameters))
        self.data = []
        place = []
        self.scaleList =  []
        for parm in numParms:
            self.data.append([])
        self.data.append([])
        
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title(self.title)
        self.ax.set_xlabel('Iterations')
        self.ax.set_ylabel('Value')
        self.ax.grid()
        self.fig.canvas.mpl_connect('pick_event', self.onpick)  
        
        output_keys = case.keys(iotype='out', flatten=True)        
        self.labels = case.keys(iotype='in', flatten=True)
        self.labels.append(output_keys[0])
        
        self.lineColors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', \
                      'b--', 'g--', 'r--', 'c--', 'm--', 'y--', 'k--', \
                      'b:', 'g:', 'r:', 'c:', 'm:', 'y:', 'k:']

        i = 0
        for line in self.data:
            self.ax.plot(place, self.data[i], self.lineColors[i], lw=2 )
            self.leg = self.ax.legend(self.labels, fancybox=True, shadow=True)
            self.leg.get_frame().set_alpha(0.6) 
            i += 1
            
        if self.logscale:
            plt.yscale('symlog')
            
    def record(self, case):
        
        self.getCount()
        if len(self.initial) == 1:        
            self.get_parameters(case)

        input_keys = case.keys(iotype='in', flatten=True)
        input_values = case.values(iotype='in', flatten=True)
        output_keys = case.keys(iotype='out', flatten=True)
        output_values = case.values(iotype='out', flatten=True)
         
        input_values.append(output_values[0])
        i = 0    
        for value in input_values:
            self.data[i].append(input_values[i])
            i += 1
            
        itNum = input_values[0]
        self.count.append(itNum)
        Iterations = len(self.count) 
        self.axis = range(0, Iterations)
        
        self.plot_on_graph()
        
    def plot_on_graph (self):

        lineList = []
        lineList = self.ax.get_lines()

        i = 0
        for dataSet in self.data:
            plt.pause(self.pause)
            lineList[i].set_xdata(self.axis)
            lineList[i].set_ydata(self.data[i])
            plt.xticks(self.axis)
            i += 1  

        newscale = self.ax.get_lines()
        self.scaleList = []

        i = 0 
        for line in newscale:
            vis = newscale[i].get_visible()
            if vis:
                current = newscale[i].get_data()
                self.scaleList.extend(current[1])
            i += 1
            
        low = min(set(self.scaleList)) - (abs(min(set(self.scaleList))) * 0.15)
        high = max(set(self.scaleList)) + (abs(max(set(self.scaleList))) * 0.15)
        self.ax.set_ylim(low, high)
        plt.draw()
        
        self.lines = lineList
        self.lined = dict()
        for legline, origline in zip(self.leg.get_lines(), self.lines):
            legline.set_picker(5)  # 5 pts tolerance
            self.lined[legline] = origline          

    def onpick(self, event):
        legline = event.artist
        origline = self.lined[legline]
        vis = not origline.get_visible()
        origline.set_visible(vis)

        if vis:
            legline.set_alpha(1.0)
        else:
            legline.set_alpha(0.2)
        self.fig.canvas.draw()            
            
    def get_iterator(self):
        self.close()
        return PlotCaseIterator(self.cases)

    def get_attributes(self, io_only=True):
        """ We need a custom get_attributes because we aren't using Traits to
        manage our changeable settings. This is unfortunate and should be
        changed to something that automates this somehow."""
        
        attrs = {}
        attrs['type'] = type(self).__name__
        variables = []
        
        attr = {}
        attr['name'] = "Pause Time"
        attr['id'] = attr['name']
        attr['type'] = type(self.pause).__name__
        attr['value'] = float(self.pause)
        attr['connected'] = ''
        attr['desc'] = 'Time duration to pause between iterations.'
        variables.append(attr)
            
        attr = {}
        attr['name'] = "Log Scale"
        attr['id'] = attr['name']
        attr['type'] = type(self.logscale).__name__
        attr['value'] = bool(self.logscale)
        attr['connected'] = ''
        attr['desc'] = 'Time duration to pause between iterations.'
        variables.append(attr)
            
        attr = {}
        attr['name'] = "Plot Title"
        attr['id'] = attr['name']
        attr['type'] = type(self.title).__name__
        attr['value'] = str(self.title)
        attr['connected'] = ''
        attr['desc'] = 'Time duration to pause between iterations.'
        variables.append(attr)
            
        attrs["Inputs"] = variables
        return attrs
        
    def close(self):
        """Does nothing."""
        plt.show()
        self.data = []
        self.axis = []
        self.count = []
        self.initial = []  
        self.scaleList =  []
        return
