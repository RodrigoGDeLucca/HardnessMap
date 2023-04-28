import streamlit as st
import pandas as pd
import numpy as np
import io
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib as mpl
import warnings
warnings.filterwarnings(‘ignore’)

mpl.rcParams['figure.dpi'] = 600

#https://discuss.streamlit.io/t/refresh-graph-datatable-inside-loop/7804

st.set_page_config(
    page_title="Hardness Map APP",
    page_icon="microscope.png",
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# Hardness Map APP. Made by *PLSC* with the base code from *WPTC*!"
    }
)

uploaded_file = st.sidebar.file_uploader("Choose the excel file with the hardness points")

enableHighlights = st.sidebar.checkbox('Enable hardness highlights')
if enableHighlights:
    highlightValue = st.sidebar.number_input('Minimum Hardness to Highlight', key=1, min_value = 0, max_value = 500, value = 350, step = 1)

enableHardness = st.sidebar.checkbox('Enable manual hardness limits')

if enableHardness:
    minValue = st.sidebar.number_input('Minimum Hardness', key=2, min_value = 0, max_value = 500, value = 200, step = 1)
    maxValue = st.sidebar.number_input('Maximum Hardness', key=3, min_value = 0, max_value = 500, value = 400, step = 1)
    #st.write('The current number is ', maxValue)

option = st.sidebar.selectbox(
    'Which interpolation should be used?',
    ('gaussian', 'nearest', 'bilinear', 'bicubic', 'spline16',
           'spline36', 'hanning', 'hamming', 'hermite', 'kaiser', 'quadric',
           'catrom',  'bessel', 'mitchell', 'sinc', 'lanczos'))


if uploaded_file != None:
    df = pd.read_excel(uploaded_file)#, encoding = "USC-2")
    #st.write(df)

    df['X1'] = round(df['X-distance to Startpoint (mm)'],0)
    df['Y1'] = -1*round(df['Y-distance to Startpoint (mm)'],0)
    df['C'] = df['Hardness']

    x1 = int(df['X1'].max()) - int(df['X1'].min()) + 1
    y1 = int(df['Y1'].max()) - int(df['Y1'].min()) + 1

    matrix = np.zeros((y1, x1))

    for index, row in df.iterrows():
        y = int(row['X1']) - int(df['X1'].min())
        x = int(row['Y1']) - int(df['Y1'].min())
        c = int(row['C'])
        matrix[x][y] = c

    
    df = pd.DataFrame(matrix)

    # %%
    #This command basically calculates the average of all its neighbors, but only if they are not equal to zero. 
    #Besides this, the calculation does not take into account a number that was already calculated using this approximation.
    new_matrix = np.copy(matrix)

    for i in range(0, y1):
        for j in range(0, x1):
            if matrix[i][j] == 0:
                num_neighbors = 0
                total = 0
                if i-1 >= 0 and matrix[i-1][j] != 0:
                    num_neighbors += 1
                    total += matrix[i-1][j]
                if i+1 < y1 and matrix[i+1][j] != 0:
                    num_neighbors += 1
                    total += matrix[i+1][j]
                if j-1 >= 0 and matrix[i][j-1] != 0:
                    num_neighbors += 1
                    total += matrix[i][j-1]
                if j+1 < x1 and matrix[i][j+1] != 0:
                    num_neighbors += 1
                    total += matrix[i][j+1]
                if num_neighbors > 0:
                    new_matrix[i][j] = total / num_neighbors


    df1 = pd.DataFrame(new_matrix)

    #df2 = df1.copy()

    #df2.replace(0, np.nan).min()
    vmin = df1.replace(0, np.nan).min(numeric_only=True).min()  # get the minimum value excluding NaN
    vmax = df1.replace(0, np.nan).max(numeric_only=True).max()

    if enableHardness:
        vmin = minValue
        vmax = maxValue

    fig, ax = plt.subplots()

    #va1 = ax.imshow(df1, cmap='RdYlGn_r', 
    #        interpolation='gaussian', 
    #        vmin=vmin, 
    #        vmax=vmax)
    va1 = ax.imshow(df1, cmap='RdYlGn_r', 
            interpolation=option, 
            vmin=vmin, 
            vmax=vmax)
    ax.set_xlabel('X Position', fontsize=13)
    ax.set_ylabel('Y Position', fontsize=13)

    #ax.add_patch(Rectangle((-0.5, -0.5), 1, 1, fill=False, edgecolor='blue', lw=3))
    
    if enableHighlights:
        for i in range(0, y1):
            for j in range(0, x1):
                if matrix[i][j] > highlightValue:
                    ax.add_patch(Rectangle((j-0.5, i-0.5), 1, 1, fill=False, edgecolor='blue', lw=1))

    if df1.shape[0] >= df1.shape[1]:
        #plt.colorbar(fig, ax=ax)
        fig.colorbar(va1, orientation='vertical')
    else:
        #plt.colorbar(fig, ax=ax)
        fig.colorbar(va1, orientation='horizontal')

    st.pyplot(fig)

    fn = 'hardness.png'
    img = io.BytesIO()

    fig.savefig(img, format='png')



    st.download_button('Download file', data=img, file_name=fn, mime="image/png")  # Defaults to 'application/octet-stream'
    #plt.show()
