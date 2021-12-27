import pandas as pd
from bokeh.plotting import figure, output_file, show
# configure visual properties on a plot's title attribute

def getFileName():
    import tkinter as tk
    from tkinter import simpledialog
    ROOT = tk.Tk()
    ROOT.withdraw()
    # the input dialog
    file = simpledialog.askstring(title="Test",
                   prompt="Enter the whole path to the filename:")
    print ('you entered:'+file)
    return file

p = figure(plot_width=2000, plot_height=650,title="Basic Title")
#p.title.text = "6350 Health when running 1,360 RPS- 750K endpoint registrations & condi.log configured"
p.title.text = "6350, 830m1p8p:  SRTP 2 RTP, 11CPS, 15 min HT"

# C:\Users\abenhida\Documents\Oracle\Backups_suites\9.0\Conditional_logging\Build 14XX\Calls\Trunk_B1430_calls_deb_ses-med_m-10k_wsize-300_request-type_INVITE.filtered.csv

p.title.align = "center"
p.title.text_color = "orange"
p.title.text_font_size = "25px"
#p.title.background_fill_color = "#aaaaee"
#p.add_layout(Title(text="Bottom Centered Title", align="center"), "below")

# prompt for the input file
output_file("6350_830m1p8p_SRTP_2_RTP_11CPS_15_min_HT.html", title="6350, 830m1p8p:  SRTP 2 RTP, 11CPS, 15 min HT")
scaleGraphBy = 2  # 100s
file = getFileName()
print ('you entered--------------:'+file)

# read the file
input_file = 'r'+'\''+file+'\''
df = pd.read_csv(file)
df2 = df.loc[:, (df != 0).any(axis=0)]  # drop all zeroes colmns
records = df.shape[0]
x = []
i=0

print(df2)
# get how many lines in the file to compute the run time, 7 sec poll interval
nlns = sum(1 for line in open(file)) -1
x.extend(range(0, nlns*7 ))

print('nlns:',nlns, '\nx:',x,'nlns * 7 =' ,nlns * 7)
clrs = ['aqua', 'aquamarine','black', 'blue', 'fuchsia', 'brown', 'burlywood', 'cadetblue', 'chartreuse', 'chocolate', 'coral', 'cornflowerblue', 'cornsilk', 'crimson', 'cyan', 'darkblue', 'darkcyan','mediumslateblue','deeppink','darkturquoise','greenyellow','lightskyblue','cadetblue', 'chartreuse', 'chocolate', 'coral', 'cornflowerblue', 'cornsilk', 'crimson', 'cyan', 'darkblue', 'darkcyan','mediumslateblue','deeppink','darkturquoise','greenyellow','lightskyblue']
for col in df2.columns:
    mx = df2[col].max()

    scaleBy = 0
    print(f"^^^^^ scaleGraphBy:{scaleGraphBy}, mx:{mx}, type:{type(mx)}")
    if mx >= 10 ** scaleGraphBy:
        scaleBy = len(str(mx)) - scaleGraphBy

    print('len(mx):',len(str(mx)),'\nscaleBy:',scaleBy,'\ndf2[col]:\n',df2[col])
    y = df2[col].apply(lambda t: t/10**scaleBy)
    print('---->col:', col, '---->y:\n', y)
    #p.circle(x, y, size=10, color='green', legend='square')
    #p.circle(x, y, size=10)
    p.xaxis[0].axis_label = 'Minutes/10'
    p.yaxis[0].axis_label = 'f(10**n)'
    # labels = LabelSet(x='weight', y='height', text='names', level='glyph',
    #                   x_offset=5, y_offset=5, source=source, render_mode='canvas')
    p.line(x, y, color=clrs[i], legend=col+': 10**'+str(scaleBy))
    i = i+1

p.legend.click_policy = 'hide'
show(p)