#!/bin/python3

import sys
import numpy as np

def get_grad_data(filename):

    S0_force_grad_data = []
    S1_force_grad_data = []
    NAC_grad_data = []

    section_count = 0
    copy = False

    with open(filename, 'r') as f:
        for line in f:
            if line.strip().startswith("* Nuclear energy gradient"):
                copy = True
                section_count += 1
            elif line.strip().startswith("- Gradient integral contraction"):
                copy = False
            elif copy == True:
                if section_count == 1:
                    S0_force_grad_data.append(line)
                if section_count == 2:
                    S1_force_grad_data.append(line)
                if section_count == 3:
                    NAC_grad_data.append(line)

    S0_force_grad_data = S0_force_grad_data[1:]
    S1_force_grad_data = S1_force_grad_data[1:]
    NAC_grad_data = NAC_grad_data[1:]

   #print(S0_force_grad_data)
   #print("------")

    return S0_force_grad_data, S1_force_grad_data, NAC_grad_data

def grads_to_vectors(grad_data):

    atoms = grad_data[0::4]
    x_raws = grad_data[1::4]
    y_raws = grad_data[2::4]
    z_raws = grad_data[3::4]


   #print(x_raws)

    vectors_list = []

    for idx in range(len(atoms)):
        x_val = float(x_raws[idx].replace('x','').strip())
        y_val = float(y_raws[idx].replace('y','').strip())
        z_val = float(z_raws[idx].replace('z','').strip())
        vector = np.array([x_val, y_val, z_val])
        vectors_list.append(vector)

        #Turn it into a matrix
        vectors = np.stack(vectors_list, axis=0)

    return vectors

#Would be more efficient with one read, but cleaner with two.
def get_geom_position(filename):

    geom_data_raw = []

    copy = False

    with open(filename, 'r') as f:
        for line in f:
            if line.strip().startswith("*** Geometry ***"): #1st instance fine
                copy=True
            elif line.strip().startswith("Number of auxiliary basis functions:"):
                copy=False
            elif copy==True:
                geom_data_raw.append(line)

    geom_data_raw = geom_data_raw[1:-1] #remove blank space

    vectors_list = []
    elem_list=[]

    for line in geom_data_raw:
        elem = line.split(',')[0].replace('{ "atom" : ','').replace('"','').strip()
        elem_list.append(elem)
        x_val = float(line.split('[')[1].split(',')[0].strip())
        y_val = float(line.split('[')[1].split(',')[1].strip())
        z_val = float(line.split('[')[1].split(',')[2].replace(']','').replace('}','').replace(',','').strip())
        vector = np.array([x_val, y_val, z_val])
        vectors_list.append(vector)

    num_atoms=len(elem_list)
   #print(elem_list)

    geom_position_matrix = np.stack(vectors_list, axis=0)
   #print(geom_position_matrix)

    return num_atoms, elem_list, geom_position_matrix

def print_xyz_file(num_atoms,elem_list,new_geom,g_step,h_step,step_size):

    outfile_name = 'g' + str(g_step) +  '_h' + str(h_step) + '.xyz'

    f = open(outfile_name, 'w')
    f.write(str(num_atoms) + '\n')
    f.write("g Step {}. h step {}. Step size {} \n".format(g_step,h_step,step_size))
    atom_idx = 0
    for atom_position in new_geom:
        f.write("  " + elem_list[atom_idx] + "  " + str(atom_position).replace('[','').replace(']','') + "\n")
        atom_idx=atom_idx+1
    f.close

    return


filename = sys.argv[1]

#Get both geom data and forces from output file
num_atoms, elem_list, geom_position_matrix = get_geom_position(filename)
S0_force_grad_data, S1_force_grad_data, NAC_grad_data = get_grad_data(filename)

#Compute vectors and normalise them
S0_force_vectors = grads_to_vectors(S0_force_grad_data)
S1_force_vectors = grads_to_vectors(S1_force_grad_data)
NAC_vectors = grads_to_vectors(NAC_grad_data)
NAC_vectors_norm = np.linalg.norm(NAC_vectors)
NAC_vectors_normalised = NAC_vectors/NAC_vectors_norm
grad_diff_vectors = S1_force_vectors - S0_force_vectors
grad_diff_norm = np.linalg.norm(grad_diff_vectors)
grad_diff_normalised = grad_diff_vectors/grad_diff_norm

#Make geometries by taking steps along both grad_diff and NAC vectors

#Sen & Schapiro, Mol. Phys. 2018, step +-0.05 Angstrom
step_size=0.01
for g_step in range(-5,5,1):
    for h_step in range(-5,5,1):
        new_geom = geom_position_matrix + grad_diff_normalised*step_size*g_step + NAC_vectors_normalised*step_size*h_step
        print_xyz_file(num_atoms,elem_list,new_geom,g_step,h_step,step_size)


"""
print("S0 Force Vectors:")
print(S0_force_vectors)

print("S1 Force Vectors:")
print(S1_force_vectors)

print("Gradient Difference Vectors:")
print(grad_diff_vectors)


print("Normalised Gradient Difference Vectors:")
print(grad_diff_normalised)

print("NAC Coupling Vectors:")
print(NAC_vectors)


print("Normalised NAC Coupling Vectors:")
print(NAC_vectors_normalised)

#print(grad_data)
#for line in grad_data:
#    print(line,)
"""
