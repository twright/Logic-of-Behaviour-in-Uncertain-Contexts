
# coding: utf-8

# In[1]:


from flowstar.reachability import Reach, Poly, get_power_4, get_factorial_rec, get_double_factorial, get_precision, set_precision

run_C = True
run_D = True

print "precision =", get_precision()
# set_precision(80)
print "precision =", get_precision()

# In[2]:

if run_C:

    varsc = [b'local_t', b't', b'x']
    pt = Poly(1, 't', 0, varsc)
    px = Poly(-1, 'x', 1, varsc)
    print "t' = {}\nx' = {}".format(pt, px)


    # In[3]:

    C = Reach(
        [b'local_t', b"t", b"x"],
        [Poly(varsc), pt, px],
        [(0,0), (5,5)],
        5,
        0.1,
        order=3,
    )


    # In[4]:


    print "res =", C.res


    # In[5]:


    print "num flowpipes =", C.num_flowpipes


    # In[6]:


    # C.wplot('t', 'x', b'res1')
    # C.plot('t', 'x', b'res1')


    # In[7]:


    # del C

# from time import sleep
# sleep(2)

print(get_factorial_rec())

# In[8]:
if run_D:

    varsd = [b'local_t', b't', b'x', b'y']
    qt = Poly(1, 't', 0, varsd)
    qx = Poly(-1, 'y', 1, varsd)
    qy = Poly(1, 'x', 1, varsd)
    # print "t' = {}\nx' = {}\ny' = {}".format(qt, qx, qy)


    # In[9]:


    print "t' = {}\nx' = {}\ny' = {}".format(qt, qx, qy)


    # In[ ]:


    D = Reach(
        varsd,
        [Poly(varsd), qt, qx, qy],
        [(0,0), (4,5), (1,2)],
        5,
        0.1,
        order=3,
    )

    print(get_factorial_rec())

    # In[21]:


    print "res =", D.res
    print "num flowpipes =", D.num_flowpipes


    # In[18]:


    # D.wplot(b'x', b'y', b'resd')
    D.plot(b'x', b'y', b'resd')


    # In[ ]:


    # del D
