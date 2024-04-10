import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

def comp_extraction(composition):                                   #組成式から炭素,水素,酸素数を抽出する関数( C9H13O3 → [9,13,3] )
    splited=re.split("C|H|O",composition)                           #CHOをそれぞれカンマ(,)に変換したリストを作成

    #酸素数の決定
    if "O" in composition:                                          #
        if splited[-1]=="":                                         #組成式に"O"を含み、リストの最後がemptyなら(つまり組成の末尾が"O"なら)
            num_O=1                                                 #酸素の数は「1」
        else:                                                       #組成式に"O"を含み、リストの最後がemptyでないなら(つまり組成の末尾が数字なら)
            num_O=int(splited[-1])                                  #酸素の数は「リストの最後の数字」
    else:                                                           #組成式に"O"が含まれていなければ
        num_O=0                                                     #酸素の数は「0」

    #炭素数の決定
    if splited[1]=="":                                              #リストの2番目がemptyなら(つまり"C"と"H"が連続していれば)
        num_C=1                                                     #炭素の数は「1」
    else:                                                           #リストの2番目が数字なら(つまり"C"と"H"が連続していなければ)
        num_C=int(splited[1])                                       #炭素の数は「リストの2番目が数字」(つまり「"C"と"H"で挟まれた数字」)

    #水素数の決定
    if splited[2]=="":                                              #リストの3番目がemptyなら(つまり"H"と"O"が連続していれば)
        num_H=1                                                     #水素の数は「1」
    else:                                                           #リストの3番目が数字なら(つまり"H"と"O"が連続していなければ)
        num_H=int(splited[2])                                       #水素の数は「リストの3番目が数字」(つまり「"H"と"O"で挟まれた数字」)
    
    return np.array([num_C,num_H,num_O])

def comp_generation(nums):                                          #炭素,水素,酸素数から組成式を作成する関数( [9,13,3] → C9H13O3 )
    if nums[0]==1:
        comp_C="C"
    else:
        comp_C="C"+str(nums[0])
    
    if nums[1]==1:
        comp_H="H"
    else:
        comp_H="H"+str(nums[1])
    
    if nums[2]==0:
        comp_O=""
    elif nums[2]==1:
        comp_O="O"
    else:
        comp_O="O"+str(nums[2])
    return comp_C+comp_H+comp_O
        
Path=st.sidebar.file_uploader('Excel')
if Path is not None:

    df=pd.read_excel(Path,index_col=0)
    df=df.dropna(subset=["Composition"])                            #STEP 1 組成不明の行を削除
    df["Composition"]=df["Composition"].str.replace(" ","")         #STEP 2 組成のスペース消去
    df["nums"]=df["Composition"].map(comp_extraction)               #STEP 345 炭素,水素,酸素数を抽出
    
    precursor_comp=st.sidebar.text_input('Precursor Composition',"CHO")  #STEP 6 プリカーサー組成式指定
    precursor_nums=comp_extraction(precursor_comp)                           #上記組成式を数字のリストに変換
    
    #STEP 7 フラグメントの組成決定
    product_comps=[]
    legends=[]
    func_groups=[]
    sort_label=[]
    if st.sidebar.checkbox("HCHO")==True:
        product_comps.append(comp_generation(precursor_nums-np.array([1,2,1])))
        legends.append("HCHO")
        func_groups.append("R-CH2OH")
        sort_label.append(1)
    if st.sidebar.checkbox("H2O")==True:
        product_comps.append(comp_generation(precursor_nums-np.array([0,2,1])))
        legends.append("H2O")
        func_groups.append("R-OH")
        sort_label.append(2)
    if st.sidebar.checkbox("CO2")==True:
        product_comps.append(comp_generation(precursor_nums-np.array([1,0,2])))
        legends.append("CO2")
        func_groups.append("R-COOH")
        sort_label.append(1.5)
    if st.sidebar.checkbox("HCOOH")==True:
        product_comps.append(comp_generation(precursor_nums-np.array([1,2,2])))
        legends.append("HCOOH")
        func_groups.append("R-COOH")
        sort_label.append(1.5)
    if st.sidebar.checkbox("H2O2")==True:
        product_comps.append(comp_generation(precursor_nums-np.array([0,2,2])))
        legends.append("H2O2")
        func_groups.append("R-OOH")
        sort_label.append(4)
    if st.sidebar.checkbox("C2H2O")==True:
        product_comps.append(comp_generation(precursor_nums-np.array([2,2,1])))
        legends.append("C2H2O")
        func_groups.append("R-COCH3")
        sort_label.append(5)
    if st.sidebar.checkbox("CO")==True:
        product_comps.append(comp_generation(precursor_nums-np.array([1,0,1])))   
        legends.append("CO")
        func_groups.append("R-CHO")
        sort_label.append(6)
    
    df=df.set_index("Composition")                                  #組成をインデックスに設定
    #df=df["Intensity"]
    df=df.loc[product_comps]                                        #STEP 7 フラグメントの抽出
    df["func_group"]=func_groups
    df["sort_label"]=sort_label
    df=df[["Intensity","func_group","sort_label"]]
    #STEP 8 円グラフ作成
    fig=plt.figure()
    percent=st.sidebar.checkbox("%")
    if percent==True:
            plt.pie(df["Intensity"],
                labels=legends,
                labeldistance=None,
                startangle=90,
                counterclock=False,
                autopct="%1.1f%%")
    else:
        plt.pie(df["Intensity"],
            labels=legends,
            labeldistance=None,
            startangle=90,
            counterclock=False)
    plt.legend(loc="center left",bbox_to_anchor=(1,0,0.5,1))
    st.pyplot(fig)
    st.write(df["Intensity"])
    
    fig=plt.figure()
    df=df.groupby("func_group").sum()
    df=df.sort_values("sort_label")
    if percent==True:
            plt.pie(df["Intensity"],
                labels=df.index,
                labeldistance=None,
                startangle=90,
                counterclock=False,
                autopct="%1.1f%%")
    else:
        plt.pie(df["Intensity"],
            labels=df.index,
            labeldistance=None,
            startangle=90,
            counterclock=False)
    plt.legend(loc="center left",bbox_to_anchor=(1,0,0.5,1))
    st.pyplot(fig)
    st.write(df["Intensity"])