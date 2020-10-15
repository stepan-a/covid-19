#!/usr/bin/env python
# coding: utf-8

# In[1]:


#Assemble images
import cv2
import numpy as np

im1 = cv2.imread('images/charts/france/incidence_taux_france.jpeg')
im2 = cv2.imread('images/charts/france/subplots_dep_incidence.jpeg')

im_h = cv2.hconcat([im1, im2])
cv2.imwrite('images/charts/france/tests_combinaison.jpeg', im_h)

im1 = cv2.imread('images/charts/france/title_incidence.jpeg')
im2 = cv2.imread('images/charts/france/tests_combinaison.jpeg')

im_h = cv2.vconcat([im1, im2])
cv2.imwrite('images/charts/france/tests_combinaison.jpeg', im_h)

