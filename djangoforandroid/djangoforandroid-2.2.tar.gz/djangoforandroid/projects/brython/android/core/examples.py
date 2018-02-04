

snippets = (

{
"name": "Simple plot",
"description": "Just a cos(t) with title and label names.",
"thumbnail": "simple.png",
"code": """
t = linspace(0, 10, 100)
y = cos(t)
plot(t, y)
xlabel("Time($s$)")
ylabel("Amplitude")
title("$cos(t)$")
"""},

{
"name": "Plot styles",
"description": "Three plots with differents line styles.",
"thumbnail": "styles.png",
"code": """
t = linspace(0, 10, 100)
y1 = cos(t)
y2 = sin(t)
y3 = sinc(t)
plot(t, y1, "b-")
plot(t, y2, "r--")
plot(t, y3, "ro")
legend(["$cos(t)$", "$sin(t)$", "$sinc(t)$"])
"""},

{
"name": "Plot themes",
"description": "Plot different theme each time.",
"thumbnail": "themes.png",
"code": """
t = linspace(0, 20, 200)
y1 = sin(t)
theme = random.choice(style.available)
figure()
style.use(theme)
plot(t, y1)
title("Theme: {}".format(theme))
grid(True)
"""},

{
"name": "Generate more than one plot",
"description": "Multiple plots in a single block",
"thumbnail": "two_plots.png",
"code": """
t = linspace(0, 10, 100)
plot(cos(t))
figure()
plot(sin(t), "b")
"""},

{
"name": "Multiplot",
"description": "Multiple plots in a single plot using subplots and grids.",
"thumbnail": "multiplot.png",
"code": """
t = linspace(0, 10, 100)

subplot(331)
plot(cos(t))
subplot(332)
plot(sin(t))
subplot(334)
plot(sinc(t))
subplot(335)
plot(tan(t))

subplot2grid((3, 3), (0, 2), rowspan=2)
plot(sin(t), t)
subplot(3, 1, 3)
plot(sin(t))
"""},

{
"name": "Surface",
"description": "Pringle surface.",
"thumbnail": "surface.png",
"code": """
n_angles = 36
n_radii = 8

# An array of radii
# Does not include radius r=0, this is to eliminate duplicate points
radii = np.linspace(0.125, 1.0, n_radii)

# An array of angles
angles = np.linspace(0, 2*np.pi, n_angles, endpoint=False)

# Repeat all angles for each radius
angles = np.repeat(angles[..., np.newaxis], n_radii, axis=1)

# Convert polar (radii, angles) coords to cartesian (x, y) coords
# (0, 0) is added here. There are no duplicate points in the (x, y) plane
x = np.append(0, (radii*np.cos(angles)).flatten())
y = np.append(0, (radii*np.sin(angles)).flatten())

# Pringle surface
z = np.sin(-x*y)

fig = plt.figure()
ax = fig.gca(projection='3d')

ax.plot_trisurf(x, y, z, cmap=matplotlib.cm.jet, linewidth=0.2)
"""},

{
"name": "Fourier transform",
"description": "Plot Fourier transform of complex signal.",
"thumbnail": "fourier.png",
"code": """
t = linspace(0, 2*pi, 2000)
y = sin(2*pi*t) + sin(2*pi*4*t) + sin(2*pi*5*t) + 2*sin(2*pi*30*t) + sin(2*pi*60*t)

#Add noise
y = array([yi + (random.random()-0.5)*5 for yi in y])

fy = fft.fft(y)
ft = fftfreq(2000, 2*pi/2000)

subplot(211)
plot(t, y, color='C0')
xlabel("Time")
ylabel("Amplitude")

subplot(212)
vlines(ft, [0], abs(fy), color="b")
xlim(-70, 70)
xlabel("Frequency")
ylabel("Amplitude")
"""},


{
"name": "Heart",
"description": "Why not?",
"thumbnail": "heart.png",
"code": """
t = arange(0, 2*pi, 0.1)

x = 16 * sin(t) ** 3
y = 13 * cos(t) - 5 * cos(2 * t) - 2 * cos(3 * t) - cos(4 * t)

for i in arange(0, 1, 0.03):
    plot(i*x, i*y, "r")

axis("off")
"""},



{
"name": "Lorenz Attractor",
"description": "Simple Lorenz attractor using scipy.integrate.odeint",
"thumbnail": "lorenz.png",
"code": """
from scipy.integrate import odeint

def lorenz(f, t=None):

    s, r, b = 10, 28, 2.667
    x, y, z = f

    x_dot = s*(y - x)
    y_dot = r*x - y - x*z
    z_dot = x*y - b*z
    return x_dot, y_dot, z_dot

soln = odeint(lorenz, [10, 10, 10], np.arange(0, 25.0, 0.01))

fig = plt.figure()
ax = fig.gca(projection='3d')
ax.plot(soln[:,0], soln[:,1], soln[:,2])

ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")
"""},


{
"name": "Pie",
"description": "So delicious.",
"thumbnail": "pie.png",
"code": """
#Top programming languages that will be most popular in 2017. [http://blog.hackerearth.com/2016/11/top-programming-language-2017.html]

labels = 'C++', 'C', 'Java', 'Python', 'C#', 'Others'
sizes = [32.24, 29.52, 18.69, 5.64, 1.87, 12.04]
explode = (0, 0, 0, 0.1, 0, 0)

fig1, ax1 = plt.subplots()
ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', shadow=False, startangle=90, colors=['C1', 'C2', 'C3', 'C4', 'C5', 'C6'])
ax1.axis('equal')
"""},


#{
#"name": "Neural network",
#"description": "",
#"thumbnail": "pybrain.png",
#"code": """
##
#"""},

{
"name": "Read files",
"description": "Read files on the Android device with 'open'.",
"thumbnail": None,
"code": """
filename =  'read_file.txt'

file = open(filename, 'r')
for line in file.readlines():
  print(line)
file.close()
"""},

{
"name": "Write files",
"description": "Write local files using 'open' function.",
"thumbnail": None,
"code": """
from datetime import datetime

filename =  'write_file.w.txt'

file = open(filename, 'w')
file.write("{}\\n".format(filename))
file.write("mode: 'w'\\n\\n")
for i in range(25):
  file.write("{}\\n".format(datetime.now()))
file.close()
"""},

{
"name": "Write files (bytes)",
"description": "Write local files using 'open' function with mode: 'wb'.",
"thumbnail": None,
"code": """
from datetime import datetime

filename =  'write_file.wb.txt'

file = open(filename, 'wb')
file.write("{}\\n".format(filename).encode())
file.write("mode: 'wb'\\n\\n".encode())
for i in range(25):
  file.write("{}\\n".format(datetime.now()).encode())
file.close()
"""},

{
"name": "Read files (bytes)",
"description": "Read files as bytes with 'open'.",
"thumbnail": None,
"code": """
filename =  'read_file.txt'

file = open(filename, 'rb')
for line in file.readlines():
  print(line)
file.close()
"""},



{
"name": "Animation",
"description": "Create an animation with Matplotlib!",
"thumbnail": "animation.png",
"code": """
def init_animation():
    global line
    line, = ax.plot(x, np.zeros_like(x), 'r.')
    ax.set_xlim(0, 2*np.pi)
    ax.set_ylim(-1, 1)

def animate(i):
    line.set_ydata(np.sin(2*np.pi*i / 50)*np.sin(x))
    return line,

fig = plt.figure()
ax = fig.add_subplot(111)
x = np.linspace(0, 2*np.pi, 100)

ani = piton_animation(fig, animate, init_func=init_animation, frames=50)
ani.show(fps=30)
"""},


{
"name": "Long code animation",
"description": "A flowers for you",
"thumbnail": "flower.png",
"code": """

import random

N = 50
fig, ax = pyplot.subplots()


#----------------------------------------------------------------------
def draw(k, xm, ym, s=1):
    """"""
    k = k[0] / k[1]
    theta = numpy.linspace(-2*numpy.pi, 2*numpy.pi, 1000)
    x = numpy.cos(k*theta) * numpy.cos(theta) + xm
    y = numpy.cos(k*theta) * numpy.sin(theta) + ym

    p, = ax.fill(x*s, y*s)
    return p


shapes = (
    (4, 1),
    (6, 1),
    (5, 2),
    (7, 2),
    (5, 3),
    (7, 3),
)



#----------------------------------------------------------------------
def random_draw():
    """"""
    shape = random.choice(shapes)
    x = random.random() * 2 * (N / 4)
    y = random.random() * (N / 4)
    s = random.random() + 0.7

    return draw(shape, x, y, s)

plots = [random_draw() for i in range(N)]


#----------------------------------------------------------------------
def aply_alpha():
    """"""
    alpha = numpy.linspace(-1, 1, len(plots))


    for plot, alpha in zip(plots, alpha):
        alpha = -abs(alpha) + 1
        plot.set_alpha(alpha)


#----------------------------------------------------------------------
def update(n):
    """"""
    plots.append(random_draw())
    plots.pop(0)
    aply_alpha()


ax.set_ylim(-5, 25)
ax.set_xlim(-5, 2*25)
ax.set_aspect('equal')
fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
ax.axis('off')

anim = piton_animation(fig, update, frames=numpy.arange(0, 100), interval=100)
anim.show()
"""},


{
"name": "Pandas: write csv",
"description": "Creating a Series by passing a list of values.",
"thumbnail": None,
"code": """
dates = pd.date_range('20130101', periods=6)
df = pd.DataFrame(np.random.randn(6,4), index=dates, columns=list('ABCD'))
df.to_csv("my_dataframe.csv")
print(df)
"""},


{
"name": "Pandas: read csv",
"description": "Read a csv file as Pandas DataFrame.",
"thumbnail": None,
"code": """
df_read = pd.read_csv("my_dataframe.csv")
print(df_read)
"""},


#{
#"name": "PyBrain",
#"description": "Building a Network.",
#"thumbnail": None,
#"code": """
#from pybrain.tools.shortcuts import buildNetwork

#net = buildNetwork(2, 3, 1)
#print(net.activate([2, 1]))
#"""},


#{
#"name": "PyBrain: Write network",
#"description": "Save current network as xml.",
#"thumbnail": None,
#"code": """
#from pybrain.tools.shortcuts import buildNetwork
#from pybrain.tools.customxml.networkwriter import NetworkWriter

#net = buildNetwork(2,4,1)
#NetworkWriter.writeToFile(net, 'filename.xml')
#"""},


#{
#"name": "PyBrain: Read network",
#"description": "Read network from xml format.",
#"thumbnail": None,
#"code": """
#from pybrain.tools.customxml.networkreader import NetworkReader

#net = NetworkReader.readFrom(open('filename.xml'))
#print(net)
#"""},

{
"name": "SymPy",
"description": "ASCII Pretty Printer.",
"thumbnail": None,
"code": """
from sympy import symbols, init_printing, Integral, pprint, sqrt
x, y, z = symbols('x y z')
init_printing()

pprint(Integral(sqrt(1/x), x))
"""},


{
"name": "Pickle: write",
"description": "Use pickle for store local data.",
"thumbnail": None,
"code": """
import pickle

x = range(10)
file = open('from_pickle.data', 'wb')

pickle.dump(x, file)
print(file.getvalue())
"""},


{
"name": "Pickle: read",
"description": "Use pickle for read data.",
"thumbnail": None,
"code": """
import pickle

file = open('from_pickle.data', 'rb')
r = pickle.load(file)

print(r)
"""},


#{
#"name": "Take a pictuare",
#"description": "Use Android backend and take a pictuare",
#"thumbnail": None,
#"code": """
#import matplotlib.image as mpimg

#pic = piton_takepictuare("test.jpg")
#data_image = mpimg.imread(pic, format='jpg')
#pyplot.axis("off")
#pyplot.imshow(data_image)
#"""},



#{
#"name": "",
#"description": "",
#"thumbnail": "",
#"code": """
##
#"""},


)


if __name__ == '__main__':

    import sys
    import os
    ##SHELL = '/home/yeison/Development/android-piton/ipiton'
    ##sys.path.append(SHELL)

    from pitoncore.pitonshell import PythonShell


    __open__ = open

    ##from shell import PythonShell
    python_shell = PythonShell('piton')
    python_shell.statement_module.__builtins__['__runfiles__'] = {}

    ##python_shell.statement_module.__builtins__['__socket__'] = None
    ##python_shell.statement_module.__builtins__['__id__'] = None


    for snippet in snippets:

        if snippet['thumbnail']:

            for index in python_shell.has_plot():
                python_shell.run('pylab.close({})'.format(index))

            python_shell.run('plt.style.use(\'seaborn-whitegrid\')')
            python_shell.run('matplotlib.rcParams[\'figure.dpi\'] = 32')

            python_shell.run('figure()')
            out = python_shell.run(snippet['code'])
            plot = python_shell.get_plot(python_shell.has_plot()[-1])

            thumbnail = os.path.join(os.path.dirname(os.path.abspath(os.curdir)), 'static', 'images', 'thumbnails', snippet['thumbnail'])
            file = __open__(thumbnail, 'wb')
            file.write(plot)
            file.close()
            os.system("mogrify -resize 50% {}".format(thumbnail))
