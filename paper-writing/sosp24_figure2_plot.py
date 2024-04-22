import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.axisartist.axislines import SubplotZero

font = {'family' : 'sans-serif',
        'weight' : 'normal',
        'size'   : 14}

matplotlib.rc('font', **font)

fig = plt.figure()
ax = SubplotZero(fig, 111)
fig.add_subplot(ax)

for direction in ["xzero"]:
    # adds arrows at the ends of each axis
    ax.axis[direction].set_axisline_style("-|>")

    # adds X and Y-axis from the origin
    ax.axis[direction].set_visible(True)
ax.axis["yzero"].set_visible(True)

for direction in ["left", "right", "bottom", "top"]:
    # hides borders
    ax.axis[direction].set_visible(False)

config_ypos = [
	2.6,
    0.6,
    1.6,
]
# Set the x-axis ticks
ax.xaxis.set_ticks([0.0, 0.5, 1.0, 1.5])
ax.set_xlim(0, 1.8)
ax.set_ylim(0, 3.8)
config_labels = [
    "LLaMA-2\n7B\n1xGPU",
    "LLaMA-2\n70B\n8xGPU",
    "Mistral\n7B\n1xGPU",
]
data = {

    "Splitwise": {
        "data": [
            1.39,
            0.09,
            0.35,
        ],
        "marker": 'o',
    },
    "LMSYS-Chat": {
        "data": [
            1.04,
            0.07,
            0.26,
        ],
        "marker": "^",
    },
    "ShareGPT": {
        "data": [
            1.64,
            0.11,
            0.41,
        ],
        "marker": "s"},
}


# Create the scatter plot with three different markers
for k, v in data.items():
	ax.scatter(v["data"], config_ypos, s=300, alpha=0.5, marker=v["marker"], label=k)

# Draw vertical and horizontal dashed lines along with boundary text
ax.axvline(x=1, linestyle='--', color='grey')
ax.text(0.3, 0.2, "compute bound")
		#verticalalignment='center', transform=plt.gca().get_yaxis_transform())
ax.text(1.2, 0.2, "memory bound")
		#verticalalignment='center', transform=plt.gca().get_yaxis_transform())
# ax.axhline(y=0.5, linestyle='--', color='grey')
#ax.text(1.02, 0.5, 'boundary', verticalalignment='center', transform=plt.gca().get_yaxis_transform())
#ax.text(1, -0.1, '$T_R = 1$', horizontalalignment='center',
#        transform=plt.gca().get_xaxis_transform())

# Hide top, left, and right spines
# for spine in ['top', 'right', 'left']:
#    plt.gca().spines[spine].set_visible(False)

# Hide y ticks and labels
ax.xaxis.set_label_text('$T_R$')

# Remove y-axis tick labels but keep the bottom spine and x-axis ticks
#ax.yaxis.set_tick_params(which='both', left=False)
# Draw y-axis labels for different config
#for cfg_id in [0,2,1]:
#    ax.text(-0.1, config_ypos[cfg_id-1], config_labels[cfg_id], horizontalalignment='right',
#            verticalalignment='center', transform=plt.gca().get_yaxis_transform())
ax.set_yticks(config_ypos, config_labels)

ax.grid()
ax.legend()

# To add an arrow to the right end of the x-axis, we use annotate
# ax.annotate('', xy=(2.0, 0), xytext=(1.8, 0),
#             arrowprops=dict(facecolor='black', arrowstyle='->'))

# Show the plot
plt.savefig("figure2.pdf", format="pdf", bbox_inches="tight")
#plt.show()
