#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from time import time
import inspect
# DEBUG = True;  #True to print all the debug, false to not print them
DEBUG = False;  #True to print all the debug, false to not print them
"""
@param M : the length
@param L : another parameter

@return : a list of the possible sets for a sum, where the index is the sum, and the value all the set corresponding
"""
def allListsBySum(M,L):
    start_time = time()
    maxNum = 5 # Numbers in the list are between 0 and maxNum
    sets = allSets(M,maxNum)
    
    res = computeAllListsBySumFromSet(sets,M)
    debugList(res)

    debug("total time : " + str(time()-start_time))
    return res


#smart debug function, the DEBUG global variable should be defined somwhere
def debug(text):
    if(DEBUG):
        print(inspect.stack()[1][3] +" : "+text)

"""this function return a set of ALL the sets of lenght M, with numbers ranging from 0 to maxNum

@param M :     number of element un each possible set
@param maxNum: maximum value for an int in the set

@return : a set of frozen set, where each contain M values. the values are of the form (value, key), with the value between 0 and maxNum
"""
def allSets(M,maxNum):
    startTime = time()
    allSetsOfLenghN = list()
    for pos in range(M):
        allSetsOfLenghN.append(set())
        if(pos==0):
            for num in range(maxNum+1):
                allSetsOfLenghN[0].add(frozenset({(num,0)}))
            continue
        for group in allSetsOfLenghN[pos-1]:
            for num in range(maxNum+1):
                newGroup = set(group)
                newNum = (num,0)  #here, num is what we are interested in, the 2nd number is a key, to avoid doublons
                while(newNum in newGroup):
                    newNum = (num,newNum[1]+1)
                newGroup.add(newNum)
                allSetsOfLenghN[pos].add(frozenset(newGroup))
    debug("time = "+str(time()-startTime))
    return allSetsOfLenghN[M-1]

"""
@param M :    number of element un each possible set
@param sets : a set returned by the function allSets

@return : a list of the possible sets for a sum, where the index is the sum, and the value all the set corresponding
"""
def computeAllListsBySumFromSet(sets,M):
    startTime = time()
    #We compute what are the possible sums
    result = [set() for i in range(M*5+1)]  # Sum_ftc is the sum 
    for se in sets:
        #We compute the sum of the set, and change it in an ordered list
        totalSum = 0
        newList = list()
        for elt in se:
            totalSum+=elt[0]
            newList.append(elt[0])
        newList.sort()
        result[totalSum].add(tuple(newList)) 
    debug("time = "+str(time()-startTime))
    return result

"""A print function to have a pretty print of the result"""
def debugList(liste):
    for i in range(len(liste)):
        debug(str(liste[i]))


# In[1]:


import numpy as np
import copy #
''' This method(task cores as host): after decide FTC and AC for each task, 
choose core with earliest available time to execute time in PL, only one task mapping for eacg FTC group'''
def task_mapping(avaiMT, M, Pred, PL, AC_F, FTC, exetime, energy, PCO_F, WCEC0, Rth0):
    import numpy as np
    fre = np.array([0.801, 0.8291, 0.8553, 0.8797, 0.9027, 1])
    fre = fre * 10 ** 9  #GHz
    vol = np.array([0.85, 0.9, 0.95, 1, 1.05, 1.1])  #voltage
    EC1 = np.array([7.3249, 8.6126, 10.238, 12.315, 14.998, 18.497])
    EC1 = EC1 * 10 ** (-9)
    lamda0 = 5 * 10 ** (-5)
    d0 = 3  #parameter of effective capacity in reliability function
    
    STALL = []  #the start time(ST) and allocation(ALL) for all tasks
    EC = []  #total energy consumption
    EC_sum = 0  #total energy consumption
    RI = []
    RI_sum = 0  #total energy consumption
    SL = 0
    fre = list(fre)
    #-------------task mapping--------------
    for task in PL:  #the currently scheduled "task"
        STALL_cur = []
        EC_cur = []
        #------------- < entry task > --------------
        avaiMT_cur = copy.deepcopy(avaiMT)
        M_index = list(range(M))
        M_FRE = [M_index, avaiMT_cur]
        #put core and avaiMT in earliest available time increasing order
        for k in range(1, len(M_FRE[1])):
            for j in range(0, len(M_FRE[1])-k):
                if M_FRE[1][j]> M_FRE[1][j+1]:
                    #'''execution %time'''
                    M_FRE[1][j], M_FRE[1][j +1] = M_FRE[1][j + 1], M_FRE[1][j]
                    M_FRE[0][j], M_FRE[0][j +1] = M_FRE[0][j + 1], M_FRE[0][j]
        #1)find core/fre for ori and dup
        if Pred[task] == []:  #entry task  
            AC_F_sum = []
            for element in AC_F[task]:
                AC_F_sum.append(element[0]+element[1])
            bfound = False
            for i in range(len(M_FRE[0])):
                for j in range(i+1,len(M_FRE[0])):
                    core_ori_index = M_FRE[0][i]
                    core_dup_index = M_FRE[0][j]
                    for item in AC_F[task]:
                        if item[1] ==0 and item[0] == FTC[core_ori_index]:  #only ori. is executed
                            #2)STALL of ori
                            fre_ori = FTC[core_ori_index]
                            st_ori = avaiMT[core_ori_index]
                            fre_ori_index = fre.index(fre_ori)
                            avaiMT[core_ori_index] = avaiMT[core_ori_index] + exetime[task][fre_ori_index]  #update avalable time fore core where ori is
                            STALL_cur.append(st_ori)  #st^o
                            STALL_cur.append(st_ori+exetime[task][fre_ori_index])  #ft^o
                            STALL_cur.append(core_ori_index)  #theta^o
                            EC_cur.append(energy[task][fre_ori_index])
                            STALL_cur.append(st_ori)  #st^d
                            STALL_cur.append(st_ori)  #ft^d
                            STALL_cur.append(core_ori_index)  #theta^d
                            EC_cur.append(0)
                            #RI
                            if WCEC0[task] != 0:
                                fi_ori = -lamda0 *10**(d0*(max(fre)-fre_ori)/(max(fre)-min(fre)) )*(WCEC0[task]/fre_ori)
                                RI.append( np.e**(fi_ori) - Rth0[task])
                            bfound = True
                            break
                        if item[1] == 0 and item[0] == FTC[core_dup_index]:  #choosing the core with earliest available time
                            #2)STALL of ori
                            core_ori_index = core_dup_index
                            fre_ori = FTC[core_ori_index]
                            st_ori = avaiMT[core_ori_index]
                            fre_ori_index = fre.index(fre_ori)
                            avaiMT[core_ori_index] = st_ori + exetime[task][fre_ori_index]  #update avalable time 
                            STALL_cur.append(st_ori)  #st^o
                            STALL_cur.append(st_ori+exetime[task][fre_ori_index])  #ft^o
                            STALL_cur.append(core_ori_index)  #theta^o
                            STALL_cur.append(st_ori)  #st^d
                            STALL_cur.append(st_ori)  #ft^d
                            STALL_cur.append(core_ori_index)  #theta^d
                            EC_cur.append(energy[task][fre_ori_index])
                            EC_cur.append(0)
                            #RI
                            if WCEC0[task] != 0:
                                fi_ori = -lamda0 *10**(d0*(max(fre)-fre_ori)/(max(fre)-min(fre)) )*(WCEC0[task]/fre_ori)
                                RI.append( np.e**(fi_ori) - Rth0[task])
                            bfound = True
                            break
                        if item[1] !=0 and item[0]+item[1] == FTC[core_ori_index]+FTC[core_dup_index]:  #both ori and dup. are executed
                            #2)STALL of ori
                            fre_ori = FTC[core_ori_index]
                            st_ori = avaiMT[core_ori_index]
                            fre_ori_index = fre.index(fre_ori)
                            avaiMT[core_ori_index] = avaiMT[core_ori_index] + exetime[task][fre_ori_index]  #update avalable time
                            STALL_cur.append(st_ori)  #st^o
                            STALL_cur.append(st_ori+exetime[task][fre_ori_index])  #ft^o
                            STALL_cur.append(core_ori_index)  #theta^o
                            EC_cur.append(energy[task][fre_ori_index])
                            #3)STALL of dup
                            fre_dup = FTC[core_dup_index]
                            st_dup = avaiMT[core_dup_index]
                            fre_dup_index = fre.index(fre_dup)
                            avaiMT[core_dup_index] = avaiMT[core_dup_index] + exetime[task][fre_dup_index]
                            STALL_cur.append(st_dup)  #st^d
                            STALL_cur.append(st_dup+exetime[task][fre_dup_index])  #ft^d
                            STALL_cur.append(core_dup_index)  #theta^d
                            EC_cur.append(energy[task][fre_dup_index])
                            #RI
                            if WCEC0[task] != 0:
                                fi_ori = -lamda0 *10**(d0*(max(fre)-fre_ori)/(max(fre)-min(fre)) )*(WCEC0[task]/fre_ori)
                                fi_dup = -lamda0 *10**(d0*(max(fre)-fre_dup)/(max(fre)-min(fre)) )*(WCEC0[task]/fre_dup)
                                RI.append(1 - (1 - np.e**(fi_ori) )*(1 - np.e**(fi_dup) ) - Rth0[task])
                            bfound = True
                            break
                    if bfound:
                        break
                if bfound:
                    break
        else:  
            #------------- < other tasks > --------------
            ##1)#-- predecessors: update avaiMT for all cores--
            max_pred = 0
            for k in Pred[task]:
                task_index = PL.index(k)
                max_pred = max(max_pred, STALL[task_index][1], STALL[task_index][4])
            avaiMT_cur = copy.deepcopy(avaiMT)
            for m in range(M):
                if avaiMT_cur[m] < max_pred:
                    avaiMT_cur[m] = max_pred
            M_index = list(range(M))
            M_FRE = [M_index, avaiMT_cur]
            #put core and avaiMT in earliest available time increasing order
            for k in range(1, len(M_FRE[1])):
                    for j in range(0, len(M_FRE[1])-k):
                        if M_FRE[1][j]> M_FRE[1][j+1]:
                            #execution %time
                            M_FRE[1][j], M_FRE[1][j + 1] = M_FRE[1][j + 1], M_FRE[1][j]
                            M_FRE[0][j], M_FRE[0][j + 1] = M_FRE[0][j + 1], M_FRE[0][j]
            #2)find core/fre for ori and dup
            AC_F_sum = []
            for element in AC_F[task]:
                AC_F_sum.append(element[0]+element[1])
            bfound = False
            for i in range(len(M_FRE[0])):
                for j in range(i+1,len(M_FRE[0])):
                    core_ori_index = M_FRE[0][i]
                    core_dup_index = M_FRE[0][j]
                    for item in AC_F[task]:
                        if item[1] == 0 and item[0] == FTC[core_ori_index]:  #choosing the core earliest available time
                            #2)STALL of ori
                            fre_ori = FTC[core_ori_index]
                            if max_pred <= avaiMT[core_ori_index]:
                                st_ori = avaiMT[core_ori_index]
                            else:
                                st_ori = max_pred
                            fre_ori_index = fre.index(fre_ori)
                            avaiMT[core_ori_index] = st_ori + exetime[task][fre_ori_index]  #update avalable time
                            STALL_cur.append(st_ori)  #st^o
                            STALL_cur.append(st_ori+exetime[task][fre_ori_index])  #ft^o
                            STALL_cur.append(core_ori_index)  #theta^o
                            STALL_cur.append(st_ori)  #st^d
                            STALL_cur.append(st_ori)  #ft^d
                            STALL_cur.append(core_ori_index)  #theta^d
                            EC_cur.append(energy[task][fre_ori_index])
                            EC_cur.append(0)
                            #RI
                            if WCEC0[task] != 0:
                                fi_ori = -lamda0 *10**(d0*(max(fre)-fre_ori)/(max(fre)-min(fre)) )*(WCEC0[task]/fre_ori)
                                RI.append( np.e**(fi_ori) - Rth0[task])
                            bfound = True
                            break
                        if item[1] == 0 and item[0] == FTC[core_dup_index]:  #choosing the core earliest available time
                            #2)STALL of ori
                            core_ori_index = core_dup_index
                            fre_ori = FTC[core_ori_index]
                            if max_pred <= avaiMT[core_ori_index]:
                                st_ori = avaiMT[core_ori_index]
                            else:
                                st_ori = max_pred
                            fre_ori_index = fre.index(fre_ori)
                            avaiMT[core_ori_index] = st_ori + exetime[task][fre_ori_index]  #update avalable time fore core where ori is
                            STALL_cur.append(st_ori)  #st^o
                            STALL_cur.append(st_ori+exetime[task][fre_ori_index])  #ft^o
                            STALL_cur.append(core_ori_index)  #theta^o
                            STALL_cur.append(st_ori)  #st^d
                            STALL_cur.append(st_ori)  #ft^d
                            STALL_cur.append(core_ori_index)  #theta^d
                            EC_cur.append(energy[task][fre_ori_index])
                            EC_cur.append(0)
                            #RI
                            if WCEC0[task] != 0:
                                fi_ori = -lamda0 *10**(d0*(max(fre)-fre_ori)/(max(fre)-min(fre)) )*(WCEC0[task]/fre_ori)
                                RI.append( np.e**(fi_ori) - Rth0[task])
                            bfound = True
                            break
                        if item[1] != 0 and item[0]+item[1] == FTC[core_ori_index]+FTC[core_dup_index]:  #both ori and dup are executed
                            #2)STALL of ori
                            fre_ori = FTC[core_ori_index]
                            if max_pred <= avaiMT[core_ori_index]:
                                st_ori = avaiMT[core_ori_index]
                            else:
                                st_ori = max_pred
                            fre_ori_index = fre.index(fre_ori)
                            avaiMT[core_ori_index] = st_ori + exetime[task][fre_ori_index]  # update avalable time
                            STALL_cur.append(st_ori)  #st^o
                            STALL_cur.append(st_ori+exetime[task][fre_ori_index])  #ft^o
                            STALL_cur.append(core_ori_index)  #theta^o
                            EC_cur.append(energy[task][fre_ori_index])
                            #4)STALL of dup
                            fre_dup = FTC[core_dup_index]
                            if max_pred <= avaiMT[core_dup_index]:
                                st_dup = avaiMT[core_dup_index]
                            else:
                                st_dup = max_pred
                            fre_dup_index = fre.index(fre_dup)
                            avaiMT[core_dup_index] = st_dup + exetime[task][fre_dup_index]
                            STALL_cur.append(st_dup)  #st^d
                            STALL_cur.append(st_dup+exetime[task][fre_dup_index])  #ft^d
                            STALL_cur.append(core_dup_index)  #theta^d
                            EC_cur.append(energy[task][fre_dup_index])
                            #RI
                            if WCEC0[task] != 0:
                                fi_ori = -lamda0 *10**(d0*(max(fre)-fre_ori)/(max(fre)-min(fre)) )*(WCEC0[task]/fre_ori)
                                fi_dup = -lamda0 *10**(d0*(max(fre)-fre_dup)/(max(fre)-min(fre)) )*(WCEC0[task]/fre_dup)
                                RI.append(1 - (1 - np.e**(fi_ori) )*(1 - np.e**(fi_dup) ) - Rth0[task])
                            bfound = True
                            break
                    if bfound:
                        break
                if bfound:
                    break
        STALL.append(STALL_cur)
        EC.append(EC_cur)
    for item in EC:
        EC_sum = EC_sum + item[0] + item[1]
    for item in RI:
        RI_sum = RI_sum + item
    RI_average = RI_sum/len(RI)
    SL = max(avaiMT)
    return STALL, EC, EC_sum, SL, RI, RI_average


# In[1]:


#-------------<bubble sort: total energy increasing order>-----------
def bubbleSort_energy_increasing(arr1, arr2, arr3):  #arr1 is PC_E, arr2 is PC_F, arr3 is PC_T
    for k in range(1, len(arr1)):
        for j in range(0, len(arr1)-k):
            if arr1[j][0] + arr1[j][1] > arr1[j+1][0] + arr1[j+1][1]:
                #energy
                arr1[j], arr1[j+1] = arr1[j+1], arr1[j]
                #frequency
                arr2[j], arr2[j+1] = arr2[j+1], arr2[j]
                #execution time
                arr3[j], arr3[j+1] = arr3[j+1], arr3[j]
    return(arr1, arr2, arr3)

