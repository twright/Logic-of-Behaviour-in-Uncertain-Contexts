
# coding: utf-8

# In[1]:


from flowstar.reachability import *


# ## Example 1

# In[2]:


vars = {b't': 0, b'x': 1}
pt = Poly(1, 't', 0, vars)
px = Poly(-1, 'x', 1, vars)
print "t' = {}\nx' = {}".format(pt, px)


# In[3]:


C = Reach(
    [b"t", b"x"],
    [pt, px],
    [(0,0), (5,5)],
    5,
    0.5,
    orders=[1, 2],
)


# In[4]:


C.run()


# In[5]:


C.num_flowpipes


# In[6]:


C.wplot('t', 'x', 'resc')


# ## Example 2

# In[7]:


varsd = {b't': 0, b'x': 1, b'y': 2}
qt = Poly(1, 't', 0, varsd)
qx = Poly(-1, 'y', 1, varsd)
qy = Poly(1, 'x', 1, varsd)
print "t' = {}\nx' = {}\ny' = {}".format(qt, qx, qy)


# In[8]:


D = Reach(
    [b't', b'x', b'y'],
    [qt, qx, qy],
    [(0,0), (4,5), (1,2)],
    5,
    0.1,
    orders=[2, 7, 7],
)


# In[12]:


D.run()


# In[10]:


D.num_flowpipes


# In[11]:


D.wplot(b'x', b'y', b'resd')

